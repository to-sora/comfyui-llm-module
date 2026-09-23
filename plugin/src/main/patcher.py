import torch
import weakref


class Patcher:
    """ModelPatcher protocol for backends owning their allocation strategy."""
    parent = None

    def __init__(self, engine):
        self._engine = weakref.ref(engine)
        self.load_device = torch.device(engine.spec["device"])
        self.offload_device = torch.device("cpu")

    @property
    def model(self):
        return self._engine()

    def model_size(self):
        return sum(b.size for b in self.model.backends) or 2 * 1024**3

    def loaded_size(self):
        if self.model.resident and self.load_device.type != "cpu":
            return self.model_size()
        return 0

    def current_loaded_device(self):
        return self.load_device if self.model.resident else self.offload_device

    def partially_load(self, device, extra_memory, force_patch_weights=False):
        before = self.loaded_size()
        self.model.load()
        return self.loaded_size() - before

    def partially_unload(self, device, memory_to_free):
        before = self.loaded_size()
        self.model.offload()
        return before

    def detach(self, unpatch_all=True):
        self.model.offload()

    def model_dtype(self):
        return torch.float16

    def model_patches_to(self, device):
        pass

    def model_patches_models(self):
        return []

    def is_clone(self, other):
        return self.model is other.model

    def is_dynamic(self):
        return False

    def lowvram_patch_counter(self):
        return 0
