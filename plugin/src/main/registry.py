from pathlib import Path
from .settings import read


def profiles():
    return read("content-config/models.yaml")


def options(model, **overrides):
    configured = profiles()
    profile = configured.get(model)
    if profile is None and Path(model).exists():
        requested = Path(model).resolve()
        for candidate in configured.values():
            target = Path(candidate["model"]).resolve()
            if requested == target or (candidate.get("backend") == "gguf" and requested == target.parent):
                profile = candidate
                break
    cfg = dict(profile or {"model": model})
    cfg["id"] = model
    cfg.setdefault("backend", "auto")
    cfg.setdefault("quantization", "bnb_nf4")
    cfg.setdefault("mmproj", "")
    cfg.setdefault("chat_template", "")
    cfg.setdefault("device", "auto")
    cfg.setdefault("kv_quantization", "none")
    cfg.setdefault("context_tokens", read("config.yaml")["context_tokens"])
    cfg.update({k: v for k, v in overrides.items() if v not in (None, "", "default")})
    if cfg["backend"] == "auto":
        cfg["backend"] = "gguf" if cfg["model"].lower().endswith(".gguf") else "transformers"
    if Path(cfg["model"]).is_dir() and not (Path(cfg["model"]) / "config.json").exists():
        raise ValueError("Select a model profile or an explicit GGUF file.")
    if cfg["backend"] == "gguf" and cfg["quantization"] == "bnb_nf4":
        cfg["quantization"] = "auto"
    return cfg
