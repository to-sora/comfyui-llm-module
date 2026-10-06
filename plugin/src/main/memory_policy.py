from comfy import model_management as mm
import torch
from .patcher import LLMPatcher
from .runtime import EVENTS


def install():
    load_models = mm.load_models_gpu

    def load(models, *args, **kwargs):
        requested = list(models)
        active = mm.loaded_models()
        llms = [m for m in requested if isinstance(m, LLMPatcher)]
        switching = any(m not in llms for m in active) if llms else any(
            isinstance(m, LLMPatcher) for m in active)
        if switching:
            before = torch.cuda.mem_get_info()[0] if torch.cuda.is_available() else 0
            mm.unload_all_models()
            after = torch.cuda.mem_get_info()[0] if torch.cuda.is_available() else 0
            EVENTS.append({"event": "switch", "to": "llm" if llms else "diffusion",
                           "cuda_free_before": before, "cuda_free_after": after})
        return load_models(requested, *args, **kwargs)

    # Runs in ComfyUI's execution path, before either backend allocates weights.
    mm.load_models_gpu = load
