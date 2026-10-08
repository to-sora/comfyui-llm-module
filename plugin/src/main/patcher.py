import weakref
import torch
from comfy import model_management as mm
from .estimate import memory_bytes, working


class LLMPatcher:
    parent = None

    def __init__(self, runtime):
        self._runtime = weakref.ref(runtime)
        self.offload_device = torch.device("cpu")
        requested = runtime.cfg["device"]
        self.load_device = mm.get_torch_device() if requested == "auto" else torch.device(requested)
        self.size = memory_bytes(runtime.cfg)

    @property
    def model(self):
        value = self._runtime()
        if value is None:
            raise RuntimeError("LLM handle has been released")
        return value

    def is_dynamic(self):
        return False

    def model_patches_models(self):
        return []

    def is_clone(self, other):
        return self is other

    def model_size(self):
        engine = self.model.engine
        if engine and engine.model is not None:
            storage = engine.diagnostics["storage"]
            return sum(storage.values()) + working(self.model.cfg, self.model.cfg["context_tokens"],
                                                  512**2 if engine.vision else 0)
        return self.size

    def loaded_size(self):
        return self.model.resident_bytes

    def current_loaded_device(self):
        return self.load_device if self.loaded_size() else self.offload_device

    def model_dtype(self):
        return getattr(torch, self.model.cfg.get("precision", "bfloat16"))

    def model_patches_to(self, device):
        pass

    def lowvram_patch_counter(self):
        return 0

    def partially_load(self, device, extra_memory, force_patch_weights=False):
        if self.loaded_size():
            return 0
        budget = min(extra_memory, mm.get_free_memory(self.load_device) * .95)
        self.model.load(str(self.load_device), budget)
        return self.loaded_size()

    def partially_unload(self, device, memory_to_free):
        return 0

    def detach(self, unpatch_all=True):
        if unpatch_all:
            self.model.offload()
