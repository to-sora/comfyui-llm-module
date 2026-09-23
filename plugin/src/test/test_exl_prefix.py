import unittest
from types import SimpleNamespace
import torch
from plugin.src.main.exl_prefix import EXLPrefix


class Backend:
    def __init__(self):
        self.spec = {'prefixes': {'assistant': 'Answer concisely.'},
                     'context_tokens': 128, 'prefix_cache_mb': 1}
        self.kv = SimpleNamespace(key_states=[torch.zeros(1, 128, 2, 4)],
            value_states=[torch.zeros(1, 128, 2, 4)], current_seq_len=0)
        self.generator = SimpleNamespace(sequence_ids=None)
        self.model = SimpleNamespace(forward=self.forward)

    def encode(self, messages, generation):
        return torch.tensor([[5, 6, 7, 8]])

    def forward(self, ids, kv, **kwargs):
        for state in kv.key_states + kv.value_states:
            state[:, :ids.shape[1]].fill_(0.5)
        kv.current_seq_len = ids.shape[1]


class EXLPrefixTests(unittest.TestCase):
    def test_prefix_survives_worker_cache_mutation(self):
        backend = Backend()
        cache = EXLPrefix(backend)
        cache.warm()
        backend.kv.key_states[0].fill_(0.9)
        cache.restore('Answer concisely.')
        self.assertTrue(torch.all(backend.kv.key_states[0][:, :4] == 0.5))
        self.assertEqual(backend.kv.current_seq_len, 4)
        self.assertEqual(cache.stats['hits'], 1)
        self.assertEqual(cache.stats['warmed'], 1)
        self.assertGreater(cache.stats['bytes'], 0)
