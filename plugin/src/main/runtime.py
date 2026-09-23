import json
import threading
import weakref
from .pool import Pool

HANDLES = weakref.WeakValueDictionary()
LOCK = threading.RLock()


def factory(cfg):
    backend = cfg["backend"]
    if backend == "auto":
        backend = "gguf" if cfg["model"].lower().endswith(".gguf") else "transformers"
    if backend == "gguf":
        from .gguf_engine import GGUFEngine
        return GGUFEngine(cfg)
    from .hf_engine import HFEngine
    return HFEngine(cfg)


class Handle:
    def __init__(self, cfg):
        from .patcher import QwenPatcher
        self.cfg = cfg
        self.pool = Pool(cfg, factory)
        self.patcher = QwenPatcher(self.pool)
        self.pool.cfg = dict(cfg, device=str(self.patcher.load_device))

    def ensure(self):
        from comfy import model_management as mm
        with LOCK:
            if self.patcher not in mm.loaded_models() or not self.pool.engines:
                mm.free_memory(1e30, self.patcher.load_device)
                mm.load_model_gpu(self.patcher)

    def generate(self, prompt, prefix, images=None, max_tokens=128, temperature=0.0,
                 prefix_cache=True):
        if max_tokens < 1 or temperature < 0:
            raise ValueError("max_tokens >= 1; temperature >= 0")
        prefix = self.cfg["prefixes"].get(prefix, prefix)
        with LOCK:
            lease = self.pool.lease(self.ensure)
            engine = lease.__enter__()
        try:
            return engine.generate(prompt, prefix, images, max_tokens, temperature, prefix_cache)
        finally:
            lease.__exit__(None, None, None)


def get_handle(cfg):
    key = json.dumps(cfg, sort_keys=True, ensure_ascii=False)
    with LOCK:
        handle = HANDLES.get(key)
        if handle is None:
            handle = Handle(cfg)
            HANDLES[key] = handle
        return handle


def status():
    import torch
    with LOCK:
        handles = list(HANDLES.values())
    return {"models": [{"model": h.cfg["model"], "mode": h.cfg["mode"],
                        **h.pool.status()} for h in handles],
            "cuda_allocated": torch.cuda.memory_allocated() if torch.cuda.is_available() else 0,
            "cuda_reserved": torch.cuda.memory_reserved() if torch.cuda.is_available() else 0}
