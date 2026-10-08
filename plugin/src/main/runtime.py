import json
import time
from collections import deque
from weakref import WeakValueDictionary
from comfy import model_management as mm
from .patcher import LLMPatcher
from .estimate import working

HANDLES = WeakValueDictionary()
EVENTS = deque(maxlen=128)


class LLMRuntime:
    def __init__(self, cfg):
        self.cfg, self.engine = cfg, None
        self.resident_bytes = self.loads = self.transfers = 0
        self.patcher = LLMPatcher(self)

    def ensure_engine(self):
        if self.cfg["backend"] != "transformers":
            raise ValueError("GGUF requires a validated HF import")
        if self.engine is None:
            from .hf_engine import HFEngine
            self.engine = HFEngine(self.cfg)

    def load(self, device, budget):
        self.ensure_engine()
        fresh = self.engine.model is None
        self.engine.load(device, budget)
        self.resident_bytes = self.engine.diagnostics["storage"].get("cuda", 0)
        self.loads += int(fresh)
        self.transfers += int(not fresh)
        EVENTS.append({"time": time.time(), "event": "loaded" if fresh else "restored",
            "model": self.cfg["id"], "resident_bytes": self.resident_bytes, "disk_loads": self.loads})

    def chat(self, request, images=None):
        self.ensure_engine()
        inputs = self.engine.prepare(request, images)
        length = inputs["input_ids"].shape[-1] + request.get("max_completion_tokens", request.get("max_tokens", 256))
        if length > self.cfg["context_tokens"]:
            raise ValueError("Prompt and reply exceed context capacity")
        pixels = sum(v.numel() for k, v in inputs.items() if k.startswith("pixel_values"))
        required = working(self.cfg, length, pixels, request.get('diagnostic_prefix'))
        mm.load_models_gpu([self.patcher], memory_required=required)
        mm.throw_exception_if_processing_interrupted()
        return self.engine.chat(request, inputs, required)

    def offload(self):
        if self.engine is None or self.engine.model is None:
            return
        self.engine.offload()
        previous = self.resident_bytes
        self.resident_bytes = self.engine.diagnostics["storage"].get("cuda", 0)
        freed = previous - self.resident_bytes
        EVENTS.append({"time": time.time(), "event": "offloaded", "model": self.cfg["id"],
                       "freed_bytes": freed, "ram_bytes": self.engine.diagnostics["storage"]["cpu"]})

    def _comfy_cache_tensors(self):
        from .residency import tensors
        if self.engine is not None and self.engine.model is not None:
            return list(tensors(self.engine.model)) + self.engine.cache_tensors()
        return []


def get_handle(cfg):
    key = json.dumps(cfg, sort_keys=True)
    handle = HANDLES.get(key)
    if handle is None:
        handle = LLMRuntime(cfg)
        HANDLES[key] = handle
    return handle


def status():
    from .runtime_status import describe
    return describe(HANDLES, EVENTS)
