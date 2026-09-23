class QwenLoader:
    CATEGORY = "Qwen/LLM"
    RETURN_TYPES = ("QWEN_MODEL",)
    FUNCTION = "load"

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "model": ("STRING", {"default": "Qwen/Qwen3.5-0.8B"}),
            "backend": (["transformers", "gguf"],),
            "quantization": (["auto", "nf4", "fp4", "int8"],),
            "mode": (["single", "concurrent"],),
        }, "optional": {
            "gguf_file": ("STRING", {"default": ""}),
            "mmproj_file": ("STRING", {"default": ""}),
        }}

    def load(self, **kwargs):
        from comfy import model_management as mm
        from .spec import normalize
        from .registry import acquire
        engine = acquire(normalize(**kwargs))
        with engine.lock:
            mm.load_models_gpu([engine.patcher], force_full_load=True)
        return (engine,)
