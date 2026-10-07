import torch
from comfy import model_management as mm


def describe(handles, events):
    return {"models": [{"model": h.cfg["id"], "loaded": h.resident_bytes > 0,
        "in_ram": h.engine is not None and h.engine.model is not None,
        "source": h.cfg["model"], "backend": "transformers", "resident_bytes": h.resident_bytes,
        "loads": h.loads, "transfers": h.transfers, "model_size": h.patcher.model_size(),
        "registry_entries": sum(p is h.patcher for p in mm.loaded_models()),
        "quantization": h.cfg["quantization"], "kv_quantization": h.cfg["kv_quantization"],
        "precision": h.cfg.get("precision", "bfloat16"),
        "diagnostics": getattr(h.engine, "diagnostics", {})} for h in list(handles.values())],
        "managed_models": [m.model.__class__.__name__ for m in mm.loaded_models()],
        "events": list(events),
        "cuda_free": torch.cuda.mem_get_info()[0] if torch.cuda.is_available() else 0,
        "cuda_allocated": torch.cuda.memory_allocated(), "cuda_reserved": torch.cuda.memory_reserved()}
