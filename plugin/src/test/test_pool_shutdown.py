import unittest
from concurrent.futures import ThreadPoolExecutor
from threading import Event
from pool_support import pool


class ShutdownTests(unittest.TestCase):
    def test_request_arriving_during_unload_reloads(self):
        runtime = pool(1)
        runtime.load()
        old = runtime.engines[0]
        closing, release = Event(), Event()
        close = old.close
        def slow_close():
            closing.set()
            if not release.wait(2):
                raise TimeoutError("test close")
            close()
        old.close = slow_close
        def request():
            with runtime.lease(runtime.load) as engine:
                return engine
        with ThreadPoolExecutor(2) as executor:
            unload = executor.submit(runtime.unload)
            self.assertTrue(closing.wait(2))
            incoming = executor.submit(request)
            release.set()
            unload.result(3)
            self.assertIsNot(incoming.result(3), old)
        self.assertEqual(runtime.active, 0)

    def test_queue_capacity_returns_after_backend_failure(self):
        runtime = pool(1)
        for _ in range(8):
            with self.assertRaises(RuntimeError):
                with runtime.lease(runtime.load):
                    raise RuntimeError("Inference cancelled")
        with runtime.lease(runtime.load):
            self.assertEqual(runtime.active, 1)
