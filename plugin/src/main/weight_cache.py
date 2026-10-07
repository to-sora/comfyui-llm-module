import re
import shutil
from pathlib import Path
from .settings import APP


def location(cfg):
    name = re.sub(r"[^\w.-]", "-", cfg["id"])[:100]
    return APP / "data/quantized" / (name + "-" + cfg["quantization"])


def source(cfg):
    path = location(cfg)
    if cfg["quantization"] == "bnb_nf4" and (path / "source.txt").is_file():
        if (path / "source.txt").read_text() == cfg["model"]:
            return str(path)
    return cfg["model"]


def save(cfg, model, processor):
    if cfg["quantization"] != "bnb_nf4" or source(cfg) != cfg["model"]:
        return
    target = location(cfg)
    staging = target.with_name(target.name + ".partial")
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(staging, safe_serialization=True, max_shard_size="2GB")
    processor.save_pretrained(staging)
    (staging / "source.txt").write_text(cfg["model"])
    if target.exists():
        shutil.rmtree(target)
    staging.rename(target)
