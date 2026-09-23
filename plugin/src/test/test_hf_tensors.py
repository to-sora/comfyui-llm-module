import tempfile
import unittest
from pathlib import Path
import torch
from PIL import Image
from plugin.src.main.settings import APP, environment, options
from plugin.src.main.hf_engine import HFEngine
from plugin.src.main.hf_inputs import prepare

environment()
from tensor_support import fixture


class HFTensorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        torch.set_num_threads(2)
        cls.tmp = tempfile.TemporaryDirectory(dir=APP / "data/tmp")
        try:
            cls.path = fixture(Path(cls.tmp.name) / "model")
        except OSError as error:
            cls.tmp.cleanup()
            raise unittest.SkipTest("Install official processor test assets") from error

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def setUp(self):
        self.cfg = options(self.path, device="cpu")
        self.engine = HFEngine(self.cfg)
        self.addCleanup(self.engine.close)
        self.prefix = self.cfg["prefixes"]["assistant"]

    def test_prefill_and_cached_generation_match_cold(self):
        self.engine.warm()
        before = self.engine.cache.bytes
        for prompt in ["Name a color.", "Describe a shape.", "列出顏色。"]:
            args = (prompt, self.prefix, None, 4, 0.0)
            cached = self.engine.generate(*args)
            self.assertEqual(cached, self.engine.generate(*args, prefix_cache=False))
        self.assertEqual(self.engine.cache.hits, 3)
        self.assertEqual(self.engine.cache.bytes, before)
        self.assertGreater(before, 0)

    def test_image_then_text_keeps_prefix_state(self):
        self.engine.warm()
        args = ("Name a color.", self.prefix, None, 4, 0.0)
        before = self.engine.generate(*args)
        red = Image.new("RGB", (64, 32), (255, 0, 0))
        self.engine.generate("Describe this image.", self.prefix, [red], 4, 0.0)
        self.assertEqual(before, self.engine.generate(*args))

    def test_context_limit_reports_before_generation(self):
        args = ("Name a color.", self.prefix, None, 8, 0.0)
        count = prepare(self.engine, self.prefix, args[0])["input_ids"].shape[-1]
        self.engine.cfg["context_tokens"] = count + 7
        with self.assertRaisesRegex(ValueError, "context_tokens"):
            self.engine.generate(*args)
