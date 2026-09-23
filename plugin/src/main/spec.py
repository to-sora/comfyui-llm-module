from .settings import defaults


def normalize(model, backend="transformers", quantization="auto", mode="single",
              gguf_file="", mmproj_file="", **overrides):
    import torch
    spec = defaults()
    spec.update(overrides)
    spec.update(model=model, backend=backend, quantization=quantization,
                mode=mode, gguf_file=gguf_file, mmproj_file=mmproj_file)
    if spec["device"] == "auto":
        spec["device"] = "cuda:0" if torch.cuda.is_available() else "cpu"
    spec.pop("startup_models", None)
    if backend not in {"transformers", "gguf"}:
        raise ValueError("backend must be transformers or gguf")
    if mode not in {"single", "concurrent"}:
        raise ValueError("mode must be single or concurrent")
    if quantization not in {"auto", "nf4", "fp4", "int8"}:
        raise ValueError("Invalid quantization selection")
    if not 1 <= int(spec["workers"]) <= 8:
        raise ValueError("workers must be between 1 and 8")
    if spec["context_tokens"] < 32 or spec["prefix_cache_mb"] <= 0:
        raise ValueError("Positive cache budget and context >=32 required")
    spec["workers"] = 1 if mode == "single" else int(spec["workers"])
    spec["prefix_cache_mb"] /= spec["workers"]
    return spec
