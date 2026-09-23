import os
from pathlib import Path

APP = Path(__file__).resolve().parents[2]


def read(name):
    import yaml
    with (APP / "config" / name).open(encoding="utf-8") as stream:
        return yaml.safe_load(stream)


def environment():
    data = APP / "data"
    for name in ("user", "input", "output"):
        (data / name).mkdir(parents=True, exist_ok=True)
    locations = {"HF_HOME": "hf", "TORCH_HOME": "torch",
                 "HF_HUB_CACHE": "hf/hub", "HUGGINGFACE_HUB_CACHE": "hf/hub",
                 "XDG_CACHE_HOME": "cache", "TMPDIR": "tmp",
                 "TRITON_CACHE_DIR": "triton", "CUDA_CACHE_PATH": "cuda",
                 "TORCHINDUCTOR_CACHE_DIR": "inductor"}
    for key, suffix in locations.items():
        path = data / suffix
        path.mkdir(parents=True, exist_ok=True)
        os.environ[key] = str(path)
    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
    os.environ["HF_HUB_DISABLE_XET"] = "1"


def options(model, backend="auto", quantization="auto", device="auto",
            mode="single", mmproj="", trust_remote_code=False):
    cfg = read("config.yaml")
    if mode not in {"single", "concurrent"}:
        raise ValueError("mode: single | concurrent")
    cfg.update(model=model, backend=backend, quantization=quantization,
               device=device, mode=mode, mmproj=mmproj,
               trust_remote_code=trust_remote_code)
    cfg["workers"] = 1 if mode == "single" else int(cfg["workers"])
    if not 1 <= cfg["workers"] <= 8:
        raise ValueError("workers: 1..8")
    if cfg["queue_limit"] < cfg["workers"] or cfg["cache_mib"] < 0:
        raise ValueError("queue_limit >= workers; cache_mib >= 0")
    cfg["prefixes"] = read("content-config/prefixes.yaml")
    return cfg
