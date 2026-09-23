import unittest
import torch
from PIL import Image
from vision_fixture import build
from plugin.src.main.messages import messages


class VisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.backend = build()
        if cls.backend is None:
            raise unittest.SkipTest('Qwen3.5 processor assets require model download')

    def test_real_template_cache_matches_uncached_generation(self):
        b = self.backend
        prefix = b.spec['prefixes']['assistant']
        inputs = b.encode(messages(prefix, 'State the sum of 2 and 3.'))
        with torch.inference_mode():
            expected = b.model.generate(**inputs, max_new_tokens=3, do_sample=False)
            b.cache.restore(inputs, prefix, False)
            actual = b.model.generate(**inputs, max_new_tokens=3, do_sample=False)
        self.assertTrue(torch.equal(expected, actual))
        self.assertGreater(b.cache.stats['hits'], 0)
        self.assertEqual(b.cache.stats['warmed'], 2)

    def test_image_prefill_after_text_request(self):
        b = self.backend
        prefix = b.spec['prefixes']['caption']
        inputs = b.encode(messages(prefix, 'Name this color.',
            [Image.new('RGB', (64, 64), 'red')]))
        b.cache.restore(inputs, prefix, True)
        self.assertNotIn('past_key_values', inputs)
        with torch.inference_mode():
            result = b.model.generate(**inputs, max_new_tokens=2, do_sample=False)
        self.assertGreater(result.shape[1], inputs['input_ids'].shape[1])
