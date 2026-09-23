from pathlib import Path
import torch
from transformers import AutoConfig, AutoModelForImageTextToText, AutoProcessor
from plugin.src.main.settings import APP

MODEL = "Qwen/Qwen3.5-0.8B"


def fixture(path):
    """Small random-weight model; real Qwen architecture and official processor."""
    torch.manual_seed(7)
    local = dict(local_files_only=True, cache_dir=str(APP / "data/hf/hub"))
    cfg = AutoConfig.from_pretrained(MODEL, **local)
    text = cfg.text_config
    text.hidden_size = 32
    text.intermediate_size = 64
    text.num_hidden_layers = 2
    text.num_attention_heads = 2
    text.num_key_value_heads = 1
    text.head_dim = 16
    text.linear_key_head_dim = text.linear_value_head_dim = 16
    text.linear_num_key_heads = text.linear_num_value_heads = 2
    text.layer_types = ["linear_attention", "full_attention"]
    text.rope_parameters["mrope_section"] = [2, 1, 1]
    vision = cfg.vision_config
    vision.depth = 1
    vision.hidden_size = vision.out_hidden_size = 32
    vision.intermediate_size = 64
    vision.num_heads = 2
    model = AutoModelForImageTextToText.from_config(cfg).eval()
    model.save_pretrained(path)
    processor = AutoProcessor.from_pretrained(MODEL, **local)
    processor.image_processor.size = {"shortest_edge": 1024, "longest_edge": 4096}
    processor.save_pretrained(path)
    return str(Path(path).resolve())
