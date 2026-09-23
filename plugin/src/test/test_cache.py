import unittest
from plugin.src.main.cache import PrefixCache


class CacheTests(unittest.TestCase):
    def test_longest_prefix_and_miss(self):
        cache = PrefixCache(32)
        cache.put([11, 22], "system", 8)
        cache.put([11, 22, 33], "extended", 8)
        self.assertEqual(cache.match([11, 22, 33, 44]), "extended")
        self.assertIsNone(cache.match([11, 23, 33, 44]))
        self.assertEqual(cache.hits, 1)

    def test_ram_budget_evicts_least_recent_prefix(self):
        cache = PrefixCache(16)
        cache.put([11], b"caption", 8)
        cache.put([22], b"assistant", 8)
        cache.match([11, 90])
        cache.put([33], b"translate", 8)
        self.assertIsNone(cache.match([22, 90]))
        self.assertEqual(cache.match([11, 90]), b"caption")
        self.assertEqual(cache.bytes, 16)

    def test_oversize_prefix_preserves_existing_cache(self):
        cache = PrefixCache(8)
        cache.put([11], b"short", 8)
        self.assertFalse(cache.put([22, 33], b"long", 16))
        self.assertEqual(cache.match([11, 90]), b"short")

    def test_replacing_prefix_accounts_for_old_bytes(self):
        cache = PrefixCache(16)
        cache.put([11], b"old", 8)
        cache.put([11], b"new", 4)
        self.assertEqual(cache.bytes, 4)
        self.assertEqual(cache.match([11, 90]), b"new")
