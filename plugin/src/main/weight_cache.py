import re
import shutil
from pathlib import Path
from .settings import APP


def location(cfg):
    name = re.sub(r"[^\w.-]", "-", cfg["model"])[:200]
    return APP / "data/quantized" / (name + "-" + cfg["quantization"])


def source(cfg):
    path = location(cfg)
    if cfg["quantization"] == "bnb_nf4":
        candidates = [path / "source.txt", *(APP / "data/quantized").glob("*/source.txt")]
        for marker in candidates:
            if marker.is_file() and marker.read_text() == cfg["model"]:
                return str(marker.parent)
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


def reservation(cfg):
    cached=source(cfg)
    if cached!=cfg['model']:
        # Saved NF4 already includes quantization metadata and unquantized tensors.
        # File sizes conservatively include headers; loader staging is separate.
        size=sum(p.stat().st_size for p in Path(cached).glob('*.safetensors'))
        if size:
            return size+512*1024**2
    from .estimate import weights
    return int(weights(cfg)*1.15)+512*1024**2


def staging(cfg, device, budget, retained):
    from .estimate import weights
    from .weight_reads import staging_bytes
    cached = source(cfg)
    scratch = staging_bytes(cached)
    if cached != cfg['model'] and str(device).startswith('cuda') and weights(cfg) <= budget:
        # Same all-GPU condition as hf_load: loading scratch precedes CPU offload.
        # Reserve the larger phase, retaining the full eventual RAM commitment.
        return max(0, scratch-retained)
    return scratch
