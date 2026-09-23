import unittest
import torch
from transformers import Qwen3Config, Qwen3ForCausalLM
from plugin.src.main.cache_tree import transfer, byte_size


class PrefixTests(unittest.TestCase):
    def test_cached_generation_matches_full_prefill(self):
        torch.manual_seed(4)
        model = Qwen3ForCausalLM(Qwen3Config(vocab_size=128, hidden_size=32,
            intermediate_size=64, num_hidden_layers=2, num_attention_heads=4,
            num_key_value_heads=2, head_dim=8)).eval()
        tokens = torch.tensor([[10, 12, 15, 17, 20, 22]])
        with torch.inference_mode():
            prefix = model(tokens[:, :3], use_cache=True).past_key_values
            ram = transfer(prefix, "cpu")
            request = transfer(ram, "cpu")
            before = byte_size(ram)
            expected = model.generate(tokens, max_new_tokens=4, do_sample=False)
            actual = model.generate(tokens, past_key_values=request,
                                     max_new_tokens=4, do_sample=False)
        self.assertTrue(torch.equal(expected, actual))
        self.assertEqual(ram.get_seq_length(), 3)
        self.assertEqual(byte_size(ram), before)
        self.assertGreater(request.get_seq_length(), 3)

    def test_recurrent_state_copy_is_request_private(self):
        from transformers import Qwen3_5TextConfig, Qwen3_5ForCausalLM
        config = Qwen3_5TextConfig(vocab_size=128, hidden_size=32,
            intermediate_size=64, num_hidden_layers=2,
            num_attention_heads=4, num_key_value_heads=2, head_dim=8,
            linear_num_key_heads=2, linear_num_value_heads=4,
            linear_key_head_dim=8, linear_value_head_dim=8,
            layer_types=["linear_attention", "full_attention"],
            partial_rotary_factor=1.0)
        model = Qwen3_5ForCausalLM(config).eval()
        tokens = torch.tensor([[10, 12, 15, 17, 20, 22]])
        with torch.inference_mode():
            cache = model(tokens[:, :3], use_cache=True).past_key_values
            saved = transfer(cache, "cpu")
            baseline = byte_size(saved)
            full = model.generate(tokens, max_new_tokens=3, do_sample=False)
            cached = model.generate(tokens, past_key_values=transfer(saved, "cpu"),
                                    max_new_tokens=3, do_sample=False)
        self.assertTrue(torch.equal(full, cached))
        self.assertEqual(saved.get_seq_length(), 3)
        self.assertEqual(byte_size(saved), baseline)
