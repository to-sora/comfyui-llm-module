import gc
import unittest
import weakref
from types import SimpleNamespace
from unittest.mock import patch
import torch
from plugin.src.main.engine import Engine
from plugin.src.main.patcher import Patcher
from plugin.src.main.spec import normalize


class Backend:
    size = 100

    def __init__(self):
        self.load_count = 0
        self.offload_count = 0

    def load(self):
        self.load_count += 1

    def offload(self):
        self.offload_count += 1


class LifecycleTests(unittest.TestCase):
    def test_unload_and_cached_handle_reload(self):
        engine = Engine.__new__(Engine)
        import threading
        engine.lock = threading.RLock()
        engine.spec = {'device': 'cpu'}
        engine.resident = False
        worker = Backend()
        engine.backends = [worker]
        adapter = Patcher(engine)
        adapter.partially_load(torch.device('cpu'), 1000)
        self.assertTrue(engine.resident)
        adapter.detach()
        self.assertFalse(engine.resident)
        adapter.partially_load(torch.device('cpu'), 1000)
        self.assertEqual(worker.load_count, 2)
        self.assertEqual(worker.offload_count, 1)

    def test_adapter_releases_orphaned_engine(self):
        engine = SimpleNamespace()
        engine = Engine.__new__(Engine)
        engine.spec = {'device': 'cpu'}
        engine.patcher = Patcher(engine)
        ref = weakref.ref(engine)
        del engine
        gc.collect()
        self.assertIsNone(ref())

    def test_invalid_model_selection_is_rejected(self):
        with self.assertRaises(ValueError):
            normalize('Qwen/Qwen3-0.6B', workers=0)
        with self.assertRaises(ValueError):
            normalize('Qwen/Qwen3-0.6B', backend='misspelled')
