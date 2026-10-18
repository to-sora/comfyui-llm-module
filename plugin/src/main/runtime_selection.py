class Selection:
    """Graph-local options referencing one process-owned weight representation."""
    def __init__(self, owner, cfg):
        self.owner, self.cfg = owner, dict(cfg)

    def chat(self, request, images=None):
        return self.owner.chat(request, images, self.cfg)

    def _comfy_cache_tensors(self):
        return self.owner._comfy_cache_tensors()
