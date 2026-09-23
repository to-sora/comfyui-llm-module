import json
import threading
from weakref import WeakValueDictionary

ENGINES = WeakValueDictionary()
STARTUP = []
LOCK = threading.RLock()


def acquire(spec):
    from .engine import Engine
    key = json.dumps(spec, sort_keys=True)
    with LOCK:
        engine = ENGINES.get(key)
        if engine is None:
            engine = Engine(spec)
            ENGINES[key] = engine
        return engine


def snapshot():
    import torch
    with LOCK:
        entries = list(ENGINES.values())
    return {"models": [e.status() for e in entries],
            "cuda_allocated": torch.cuda.memory_allocated()
            if torch.cuda.is_available() else 0}
