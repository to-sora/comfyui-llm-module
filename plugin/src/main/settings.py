import os
from pathlib import Path
import yaml

APP = Path(__file__).resolve().parents[2]


def read(name):
    with (APP / "config" / name).open(encoding="utf-8") as stream:
        return yaml.safe_load(stream)


def environment():
    locations = {"HF_HOME": "hf", "HF_HUB_CACHE": "hf/hub",
                 "HUGGINGFACE_HUB_CACHE": "hf/hub", "TORCH_HOME": "torch",
                 "XDG_CACHE_HOME": "cache", "TMPDIR": "tmp",
                 "TRITON_CACHE_DIR": "triton", "CUDA_CACHE_PATH": "cuda",
                 "TORCHINDUCTOR_CACHE_DIR": "inductor"}
    for name in ("user", "input", "output"):
        (APP / "data" / name).mkdir(parents=True, exist_ok=True)
    for key, suffix in locations.items():
        path = APP / "data" / suffix
        path.mkdir(parents=True, exist_ok=True)
        os.environ[key] = str(path)
    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
    os.environ["HF_HUB_DISABLE_XET"] = "1"
