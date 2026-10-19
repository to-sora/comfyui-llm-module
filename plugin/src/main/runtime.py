import time
from collections import deque
from .patcher import LLMPatcher
from . import ram_budget
from .runtime_selection import Selection

HANDLES = {}
EVENTS = deque(maxlen=128)


class LLMRuntime:
    def __init__(self, cfg, key):
        self.cfg, self.engine = cfg, None
        self.key = key
        self.resident_bytes = self.loads = self.transfers = 0
        self.patcher = LLMPatcher(self)

    def ensure_engine(self):
        if self.cfg["backend"] != "transformers":
            raise ValueError("GGUF requires a validated HF import")
        if self.engine is None:
            from .hf_engine import HFEngine
            self.engine = HFEngine(self.cfg)

    def load(self, device, budget):
        from .runtime_loading import load
        load(self, device, budget, EVENTS)

    def chat(self, request, images, cfg):
        from .runtime_chat import chat
        return chat(self, request, images, cfg)

    def offload(self):
        if self.engine is None or self.engine.model is None:
            return
        ram_budget.check(self.resident_bytes, floor=ram_budget.FLOOR+512*1024**2)
        self.engine.offload()
        previous = self.resident_bytes
        self.resident_bytes = self.engine.diagnostics["storage"].get("cuda", 0)
        ram_budget.update(self.key, sum(self.engine.diagnostics['storage'].values()), self.resident_bytes)
        freed = previous - self.resident_bytes
        EVENTS.append({"time": time.time(), "event": "offloaded", "model": self.cfg["id"],
                       "freed_bytes": freed, "ram_bytes": self.engine.diagnostics["storage"]["cpu"]})

    def _comfy_cache_tensors(self):
        from .residency import tensors
        if self.engine is not None and self.engine.model is not None:
            return list(tensors(self.engine.model)) + self.engine.cache_tensors()
        return []


def get_handle(cfg):
    from .runtime_identity import canonical
    cfg, key = canonical(cfg)
    with ram_budget.LOCK:
        if key not in HANDLES:
            HANDLES[key] = LLMRuntime(dict(cfg),key)
        return Selection(HANDLES[key],cfg)


def status():
    from .runtime_status import describe
    return describe(HANDLES, EVENTS)
