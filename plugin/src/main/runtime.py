import json
import time
import weakref
from collections import deque
import torch
from comfy import model_management as mm
from .patcher import LLMPatcher

HANDLES = weakref.WeakValueDictionary()
EVENTS = deque(maxlen=64)


class LLMRuntime:
    def __init__(self, cfg):
        self.cfg = cfg
        self.engine = None
        self.resident_bytes = 0
        self.loads = 0
        self.patcher = LLMPatcher(self)

    def load(self, device):
        before = torch.cuda.mem_get_info()[0] if device.startswith("cuda") else 0
        cfg = dict(self.cfg, device=device)
        if cfg["backend"] == "gguf":
            from .gguf_engine import GGUFEngine
            self.engine = GGUFEngine(cfg)
        else:
            from .hf_engine import HFEngine
            self.engine = HFEngine(cfg)
        if device.startswith("cuda"):
            torch.cuda.synchronize()
            self.resident_bytes = max(0, before - torch.cuda.mem_get_info()[0])
        self.loads += 1
        EVENTS.append({"time": time.time(), "event": "loaded", "model": cfg["id"],
                       "resident_bytes": self.resident_bytes, "load": self.loads})

    def chat(self, request, images=None):
        if self.engine is None or self.patcher not in mm.loaded_models():
            mm.load_models_gpu([self.patcher], memory_required=1024**3)
        mm.throw_exception_if_processing_interrupted()
        return self.engine.chat(request, images)

    def close(self):
        if self.engine is None:
            return
        self.engine.close()
        self.engine = None
        self.resident_bytes = 0
        EVENTS.append({"time": time.time(), "event": "unloaded", "model": self.cfg["id"]})


def get_handle(cfg):
    key = json.dumps(cfg, sort_keys=True)
    handle = HANDLES.get(key)
    if handle is None:
        handle = LLMRuntime(cfg)
        HANDLES[key] = handle
    return handle


def status():
    return {"models": [{"model": h.cfg["id"], "loaded": h.engine is not None,
                        "source": h.cfg["model"], "backend": h.cfg["backend"],
                        "resident_bytes": h.resident_bytes, "loads": h.loads,
                        "quantization": h.cfg["quantization"],
                        "kv_quantization": h.cfg["kv_quantization"],
                        "diagnostics": getattr(h.engine, "diagnostics", {})}
                       for h in list(HANDLES.values())],
            "managed_models": [m.model.__class__.__name__ for m in mm.loaded_models()],
            "events": list(EVENTS),
            "cuda_free": torch.cuda.mem_get_info()[0] if torch.cuda.is_available() else 0,
            "cuda_allocated": torch.cuda.memory_allocated(),
            "cuda_reserved": torch.cuda.memory_reserved()}
