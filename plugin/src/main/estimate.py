import json
from functools import lru_cache
from pathlib import Path
from huggingface_hub import hf_hub_download
from .settings import APP


@lru_cache(maxsize=24)
def metadata(source):
    path = Path(source)
    if path.is_file():
        raise ValueError("Import GGUF into a validated HF repository before inference")
    config_path = path / "config.json" if path.is_dir() else Path(hf_hub_download(
        source, "config.json", cache_dir=str(APP / "data/hf/hub")))
    config = json.loads(config_path.read_text())
    index = path / "model.safetensors.index.json"
    if index.is_file():
        size = json.loads(index.read_text())["metadata"]["total_size"]
    elif path.is_dir():
        size = sum(p.stat().st_size for p in path.glob("*.safetensors"))
    else:
        text = config.get("text_config", config)
        size = (12 * text["num_hidden_layers"] * text["hidden_size"]**2
                + text["vocab_size"] * text["hidden_size"]) * 2
    return config, size


def weights(cfg):
    _, size = metadata(cfg["model"])
    ratio = {"bnb_nf4": 0.34, "bnb_fp4": 0.34, "bnb_int8": 0.6}.get(cfg["quantization"], 1)
    return int(size * ratio)


def working(cfg, tokens, pixels=0):
    config, _ = metadata(cfg["model"])
    t = config.get("text_config", config)
    layers = t.get("layer_types", ["full_attention"] * t["num_hidden_layers"])
    heads = t.get("num_key_value_heads", t["num_attention_heads"])
    dim = t.get("head_dim", t["hidden_size"] // t["num_attention_heads"])
    per = {"hqq_4": .625, "hqq_8": 1.125}.get(cfg["kv_quantization"], 2)
    kv = 0
    for kind in layers:
        if kind == "linear_attention":
            kv += t["linear_num_value_heads"] * t["linear_key_head_dim"] * t["linear_value_head_dim"] * 4
        else:
            length = min(tokens, t.get("sliding_window", tokens) or tokens) if kind == "sliding_attention" else tokens
            kv += 2 * length * heads * dim * per
    compute = tokens * t["hidden_size"] * 16 + pixels * 24 + 256 * 1024**2
    return int(kv + compute)


def memory_bytes(cfg):
    return weights(cfg) + working(cfg, cfg["context_tokens"], 512**2 if "vision_config" in metadata(cfg["model"])[0] else 0)
