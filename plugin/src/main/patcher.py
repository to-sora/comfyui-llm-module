import gc
import torch
from comfy import model_management as mm
from .estimate import memory_bytes


class LLMPatcher:
    parent = None

    def __init__(self, runtime):
        self.model = runtime
        self.offload_device = torch.device("cpu")
        requested = runtime.cfg["device"]
        self.load_device = mm.get_torch_device() if requested == "auto" else torch.device(requested)
        self.size = memory_bytes(runtime.cfg)

    def is_dynamic(self):
        return False

    def model_patches_models(self):
        return []

    def is_clone(self, other):
        return False

    def model_size(self):
        return self.size

    def loaded_size(self):
        return self.model.resident_bytes if self.model.engine is not None else 0

    def current_loaded_device(self):
        return self.load_device if self.model.engine is not None else self.offload_device

    def model_dtype(self):
        return torch.bfloat16

    def model_patches_to(self, device):
        pass

    def lowvram_patch_counter(self):
        return 0

    def partially_load(self, device, extra_memory, force_patch_weights=False):
        if self.model.engine is not None:
            return 0
        self.model.load(str(self.load_device))
        self.size = max(self.size, self.loaded_size())
        return self.loaded_size()

    def partially_unload(self, device, memory_to_free):
        before = self.loaded_size()
        self.detach()
        return before

    def detach(self, unpatch_all=True):
        self.model.close()
        gc.collect()
        mm.soft_empty_cache()
