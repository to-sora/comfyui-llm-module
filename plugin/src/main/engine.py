import gc
import threading
from concurrent.futures import ThreadPoolExecutor
from queue import Queue


class Engine:
    def __init__(self, spec):
        from .patcher import Patcher
        from .gguf_backend import GGUFBackend
        from .tensor_backend import TensorBackend
        from .exl_backend import EXLBackend
        self.spec = spec
        self.lock = threading.RLock()
        backend = {"gguf": GGUFBackend, "transformers": TensorBackend,
                   "exl2": EXLBackend}[spec["backend"]]
        self.backends = [backend(spec) for _ in range(spec["workers"])]
        self.resident = False
        self.patcher = Patcher(self)

    def load(self):
        with self.lock:
            if not self.resident:
                try:
                    for backend in self.backends:
                        backend.load()
                    self.resident = True
                except BaseException:
                    self.offload()
                    raise

    def offload(self):
        with self.lock:
            for backend in self.backends:
                backend.offload()
            self.resident = False
            gc.collect()
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

    def generate(self, prompts, prefix, images, tokens, temperature):
        from .lifecycle import ensure_loaded
        from .interrupt import check_interrupt
        with self.lock:
            ensure_loaded(self)
            available = Queue()
            for backend in self.backends:
                available.put(backend)

            def run(prompt):
                check_interrupt()
                backend = available.get()
                try:
                    return backend.generate(prompt, prefix, images,
                                            tokens, temperature)
                finally:
                    available.put(backend)

            with ThreadPoolExecutor(max_workers=len(self.backends)) as pool:
                return list(pool.map(run, prompts))

    def status(self):
        return {"model": self.spec["model"], "mode": self.spec["mode"],
                "backend": self.spec["backend"], "resident": self.resident,
                "device": self.spec["device"], "workers": len(self.backends),
                "weight_bytes": sum(b.size for b in self.backends),
                "prefix": [b.cache.stats.copy() if b.cache else {}
                           for b in self.backends]}
