from contextlib import contextmanager
from threading import BoundedSemaphore, Condition


class Pool:
    def __init__(self, cfg, factory):
        self.cfg, self.factory = cfg, factory
        self.cv = Condition()
        self.gate = BoundedSemaphore(cfg["queue_limit"])
        self.engines, self.idle = [], []
        self.active = self.peak_active = 0
        self.closing = False

    def load(self):
        with self.cv:
            if self.engines:
                return
            try:
                for _ in range(self.cfg["workers"]):
                    engine = self.factory(self.cfg)
                    self.engines.append(engine)
                    engine.warm()
                self.idle = self.engines.copy()
            except BaseException:
                for engine in self.engines:
                    engine.close()
                self.engines.clear()
                raise

    @contextmanager
    def lease(self, ensure):
        if not self.gate.acquire(blocking=False):
            raise RuntimeError("Request queue full / 請求佇列已滿")
        engine = None
        try:
            with self.cv:
                ready = self.cv.wait_for(lambda: not self.closing,
                                         self.cfg["queue_timeout"])
                if not ready:
                    raise TimeoutError("Model unload timeout")
                ensure()
                ready = self.cv.wait_for(lambda: self.idle and not self.closing,
                                         self.cfg["queue_timeout"])
                if not ready:
                    raise TimeoutError("Request queue timeout / 請求等候逾時")
                engine = self.idle.pop()
                self.active += 1
                self.peak_active = max(self.peak_active, self.active)
            yield engine
        finally:
            with self.cv:
                if engine is not None:
                    self.idle.append(engine)
                    self.active -= 1
                self.cv.notify_all()
            self.gate.release()

    def unload(self):
        with self.cv:
            self.closing = True
            try:
                self.cv.wait_for(lambda: self.active == 0)
                for engine in self.engines:
                    engine.close()
                self.engines.clear()
                self.idle.clear()
            finally:
                self.closing = False
                self.cv.notify_all()

    def status(self):
        with self.cv:
            return {"loaded": bool(self.engines), "active": self.active,
                    "peak_active": self.peak_active,
                    "workers": len(self.engines),
                    "prefix_bytes": sum(e.cache.bytes for e in self.engines),
                    "prefix_hits": sum(e.cache.hits for e in self.engines)}
