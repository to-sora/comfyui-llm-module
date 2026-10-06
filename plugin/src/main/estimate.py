import json
from pathlib import Path
from huggingface_hub import hf_hub_download
from .settings import APP


def memory_bytes(cfg):
    path = Path(cfg["model"])
    if cfg["backend"] == "gguf":
        size = path.stat().st_size
        if cfg["mmproj"]:
            size += Path(cfg["mmproj"]).stat().st_size
        return size + 512 * 1024**2
    index = path / "model.safetensors.index.json"
    if index.is_file():
        size = json.loads(index.read_text())["metadata"]["total_size"]
    elif path.is_dir():
        size = sum(p.stat().st_size for p in path.glob("*.safetensors"))
    else:
        index = hf_hub_download(cfg["model"], "config.json",
                               cache_dir=str(APP / "data/hf/hub"))
        config = json.loads(Path(index).read_text())
        text = config.get("text_config", config)
        width = text["hidden_size"]
        size = (12 * text["num_hidden_layers"] * width**2
                + text["vocab_size"] * width) * 2
    ratio = {"bnb_nf4": 0.32, "bnb_fp4": 0.32, "bnb_int8": 0.58}.get(
        cfg["quantization"], 1.0)
    return int(size * ratio + 512 * 1024**2)
