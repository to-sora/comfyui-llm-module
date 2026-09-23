import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
from unittest.mock import patch
from plugin.src.main.engine import Engine


class Worker:
    size = 1
    cache = None

    def __init__(self, gate):
        self.gate = gate
        self.running = False

    def generate(self, prompt, *args):
        assert not self.running
        self.running = True
        self.gate.wait(timeout=3)
        time.sleep(0.02)
        self.running = False
        return prompt.upper()

    def load(self):
        pass

    def offload(self):
        assert not self.running


class ConcurrencyTests(unittest.TestCase):
    def test_overlapping_work_preserves_order_and_unload_waits(self):
        engine = Engine.__new__(Engine)
        engine.lock = threading.RLock()
        engine.resident = False
        engine.patcher = object()
        engine.backends = [Worker(threading.Barrier(2)) for _ in range(2)]
        engine.backends[1].gate = engine.backends[0].gate
        mm = SimpleNamespace(load_models_gpu=lambda *a, **k: engine.load(),
            current_loaded_models=[],
            throw_exception_if_processing_interrupted=lambda: None)
        with patch.dict('sys.modules', {'comfy': SimpleNamespace(model_management=mm),
                                       'comfy.model_management': mm}):
            with ThreadPoolExecutor(max_workers=2) as pool:
                job = pool.submit(engine.generate, ['a', 'b', 'c', 'd'], '', None, 8, 0)
                deadline = time.monotonic() + 3
                while not engine.backends[0].running and time.monotonic() < deadline:
                    time.sleep(0.001)
                release = pool.submit(engine.offload)
                self.assertEqual(job.result(timeout=5), ['A', 'B', 'C', 'D'])
                release.result(timeout=5)
        self.assertFalse(engine.resident)

    def test_single_mode_uses_one_worker(self):
        from plugin.src.main.spec import normalize
        self.assertEqual(normalize('Qwen/Qwen3-0.6B', mode='single')['workers'], 1)
