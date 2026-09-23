import os
from pathlib import Path

APP = Path(__file__).resolve().parents[2]
ROOT = APP.parent
DATA = APP / "data"


def configure_paths():
    DATA.mkdir(parents=True, exist_ok=True)
    for key, folder in {
        "HF_HOME": "hf", "TORCH_HOME": "torch", "XDG_CACHE_HOME": "cache",
        "TMPDIR": "tmp", "NUMBA_CACHE_DIR": "numba",
    }.items():
        path = DATA / folder
        path.mkdir(exist_ok=True)
        os.environ[key] = str(path)
    os.environ["HF_HUB_DISABLE_XET"] = "1"
    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"


def read_config(name="config.yaml"):
    import yaml
    with (APP / "config" / name).open(encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def defaults():
    config = read_config()
    config["prefixes"] = read_config("content-config/prefixes.yaml")
    return config
