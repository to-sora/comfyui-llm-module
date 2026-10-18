import torch
from . import background_model


class BackgroundPatcher:
    parent=None
    offload_device=load_device=torch.device('cpu')
    active=False

    @property
    def model(self):
        return self

    def is_dynamic(self):
        return False

    def model_patches_models(self):
        return []

    def is_clone(self,other):
        return self is other

    def model_size(self):
        return 256*1024**2

    def loaded_size(self):
        return self.model_size() if self.active else 0

    def current_loaded_device(self):
        return self.load_device

    def model_dtype(self):
        return torch.float32

    def model_patches_to(self,device):
        pass

    def lowvram_patch_counter(self):
        return 0

    def partially_load(self,device,extra_memory,force_patch_weights=False):
        background_model.load()
        self.active=True
        return self.loaded_size()

    def partially_unload(self,device,memory_to_free):
        return 0

    def detach(self,unpatch_all=True):
        if unpatch_all:
            self.active=False


PATCHER=BackgroundPatcher()
