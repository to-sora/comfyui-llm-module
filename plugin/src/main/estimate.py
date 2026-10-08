import json
from transformers import AutoConfig
from functools import lru_cache
from pathlib import Path
from huggingface_hub import hf_hub_download
from .settings import APP
from .weight_estimate import parameter_counts


@lru_cache(maxsize=24)
def metadata(source):
    path = Path(source)
    if path.is_file():
        raise ValueError("Import GGUF into a validated HF repository before inference")
    config_path = path / "config.json" if path.is_dir() else Path(hf_hub_download(
        source, "config.json", cache_dir=str(APP / "data/hf/hub")))
    config = AutoConfig.from_pretrained(config_path.parent, local_files_only=True,
                                       trust_remote_code=False).to_dict()
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
    config, size = metadata(cfg["model"])
    if cfg["quantization"] not in ("bnb_nf4", "bnb_fp4", "bnb_int8") or config.get("quantization_config"):
        return size
    linear, other = parameter_counts(cfg["model"])
    per = 1.01 if cfg["quantization"] == "bnb_int8" else .516
    return int((linear * per + other * 2) * 1.02)


def working(cfg, tokens, pixels=0, diagnostic=None):
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
    if diagnostic:
        from .prefix_probe_budget import extra
        compute += extra(t, tokens, diagnostic)
    return int(kv + compute)


def memory_bytes(cfg):
    return weights(cfg) + working(cfg, cfg["context_tokens"], 512**2 if "vision_config" in metadata(cfg["model"])[0] else 0)
