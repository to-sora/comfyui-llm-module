import gc


class QwenPatcher:
    parent = None

    def __init__(self, pool):
        import torch
        from comfy import model_management as mm
        self.model = pool
        self.offload_device = torch.device("cpu")
        requested = pool.cfg["device"]
        self.load_device = mm.get_torch_device() if requested == "auto" else torch.device(requested)

    def is_dynamic(self):
        return False

    def model_patches_models(self):
        return []

    def is_clone(self, other):
        return False

    def model_size(self):
        return sum(e.weight_bytes for e in self.model.engines)

    def loaded_size(self):
        return self.model_size() if self.load_device.type != "cpu" else 0

    def current_loaded_device(self):
        return self.load_device if self.model.engines else self.offload_device

    def model_dtype(self):
        import torch
        return torch.float16

    def model_patches_to(self, device):
        pass

    def lowvram_patch_counter(self):
        return 0

    def partially_load(self, device, extra_memory, force_patch_weights=False):
        before = self.loaded_size()
        self.model.load()
        return self.loaded_size() - before

    def partially_unload(self, device, memory_to_free):
        before = self.loaded_size()
        self.detach()
        return before

    def detach(self, unpatch_all=True):
        self.model.unload()
        gc.collect()
        from comfy import model_management as mm
        mm.soft_empty_cache()
