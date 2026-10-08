from comfy import model_management as mm
from .nodes_load import LLMModel
from .nodes_generate import LLMChat
from .batch_noise import LLMBatchNoise


class LLMUnload:
    CATEGORY = "LLM"
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
        mm.unload_all_models()
        mm.soft_empty_cache()
        return (after,)


NODE_CLASS_MAPPINGS = {c.__name__: c for c in (LLMModel, LLMChat, LLMUnload, LLMBatchNoise)}
