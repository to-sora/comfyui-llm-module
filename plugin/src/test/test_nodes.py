import json
import unittest
from plugin.src.main.nodes_generate import QwenBatch
from plugin.src.main.gguf_files import chat_prefix


class Handle:
    cfg = {"queue_limit": 4, "workers": 2}

    def generate(self, prompt, prefix, images, tokens, temp, cache):
        return prompt.upper()


class NodeTests(unittest.TestCase):
    def test_batch_preserves_input_order(self):
        result = QwenBatch().generate(Handle(), '["red","blue"]', "assistant", 8, 0)
        self.assertEqual(json.loads(result["result"][0]), ["RED", "BLUE"])
        self.assertEqual(result["ui"]["text"], ["RED", "BLUE"])

    def test_batch_overload_reports_queue_limit(self):
        with self.assertRaisesRegex(ValueError, "queue_limit"):
            QwenBatch().generate(Handle(), json.dumps(["hello"] * 5), "assistant", 8, 0)

    def test_chatml_prefix_keeps_message_boundary(self):
        self.assertEqual(chat_prefix("hello"), "<|im_start|>system\nhello<|im_end|>\n")
