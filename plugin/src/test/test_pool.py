import unittest
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, Event
from pool_support import Engine, pool


class PoolTests(unittest.TestCase):
    def test_concurrent_requests_receive_distinct_engines(self):
        runtime = pool()
        overlap = Barrier(2)
        def run():
            with runtime.lease(runtime.load) as engine:
                overlap.wait(timeout=2)
                return id(engine)
        with ThreadPoolExecutor(2) as executor:
            a, b = list(executor.map(lambda _: run(), range(2)))
        self.assertNotEqual(a, b)
        self.assertEqual(runtime.peak_active, 2)
        self.assertEqual(runtime.status()["prefix_bytes"], 10)

    def test_single_mode_reuses_one_engine(self):
        runtime = pool(1)
        def run(_):
            with runtime.lease(runtime.load) as engine:
                return id(engine)
        with ThreadPoolExecutor(4) as executor:
            ids = list(executor.map(run, range(4)))
        self.assertEqual(len(set(ids)), 1)
        self.assertEqual(runtime.peak_active, 1)

    def test_unload_waits_for_inference_and_then_reloads(self):
        runtime = pool(1)
        entered, finish = Event(), Event()
        def run():
            with runtime.lease(runtime.load) as engine:
                entered.set()
                self.assertTrue(finish.wait(2))
                self.assertFalse(engine.closed)
                return engine
        with ThreadPoolExecutor(2) as executor:
            active = executor.submit(run)
            self.assertTrue(entered.wait(2))
            unloading = executor.submit(runtime.unload)
            self.assertFalse(unloading.done())
            finish.set()
            old = active.result(3)
            unloading.result(3)
        self.assertTrue(old.closed)
        with runtime.lease(runtime.load) as current:
            self.assertIsNot(old, current)

    def test_failed_generation_releases_slot(self):
        runtime = pool(1)
        with self.assertRaises(RuntimeError):
            with runtime.lease(runtime.load):
                raise RuntimeError("CUDA out of memory")
        with runtime.lease(runtime.load):
            self.assertEqual(runtime.active, 1)

    def test_failed_prefill_rolls_back_loaded_engines(self):
        runtime = pool(1)
        engine = Engine({})
        def failed():
            raise RuntimeError("CUDA out of memory")
        engine.warm = failed
        runtime.factory = lambda cfg: engine
        with self.assertRaises(RuntimeError):
            runtime.load()
        self.assertTrue(engine.closed)
        self.assertEqual(runtime.engines, [])
