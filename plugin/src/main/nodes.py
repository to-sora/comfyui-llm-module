from .nodes_load import QwenModel
from .nodes_generate import QwenGenerate, QwenBatch


class QwenUnload:
    CATEGORY = "Qwen"
    RETURN_TYPES = ("STRING",)
    FUNCTION = "unload"
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"after": ("STRING", {"forceInput": True})}}

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("nan")

    def unload(self, after):
        from comfy import model_management as mm
        mm.unload_all_models()
        mm.soft_empty_cache()
        return (after,)


NODE_CLASS_MAPPINGS = {c.__name__: c for c in
                       (QwenModel, QwenGenerate, QwenBatch, QwenUnload)}
