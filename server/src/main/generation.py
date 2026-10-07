import math
import secrets
import yaml
from .settings import APP
from .errors import UserError


def recipe():
    return yaml.safe_load((APP / "config/content-config/generation.yaml").read_text())


def defaults():
    r = recipe()
    return {**{k: r[k] for k in ("steps", "cfg", "sampler_name", "scheduler", "aspect")},
            "width": 1024, "height": 1024, "seed": None, "denoise": 0.5,
            "prompt": "", "negative": ""}


def seed(value=None):
    if value in (None, "", "random", -1, "-1"):
        return secrets.randbits(63)
    try:
        result = int(value)
    except (TypeError, ValueError) as exc:
        raise UserError("Seed must be an integer or left empty for random") from exc
    if not 0 <= result <= 2**64 - 1:
        raise UserError("Seed must be between 0 and 18446744073709551615")
    return result


def source_size(size):
    scale = math.sqrt(1024**2 / (size[0] * size[1]))
    scale = min(scale, 4096 / max(size))
    return tuple(max(16, min(4096, round(n * scale / 8) * 8)) for n in size)
