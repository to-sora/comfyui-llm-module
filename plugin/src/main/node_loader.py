class QwenLoader:
    CATEGORY = "Qwen/LLM"
    RETURN_TYPES = ("QWEN_MODEL",)
    FUNCTION = "load"

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "model": ("STRING", {"default": "Qwen/Qwen3.5-0.8B"}),
            "backend": (["transformers", "gguf", "exl2"],),
            "quantization": (["auto", "nf4", "fp4", "int8"],),
            "mode": (["single", "concurrent"],),
        }, "optional": {
            "gguf_file": ("STRING", {"default": ""}),
            "mmproj_file": ("STRING", {"default": ""}),
        }}

    def load(self, **kwargs):
        from .lifecycle import ensure_loaded
        from .spec import normalize
        from .registry import acquire
        engine = acquire(normalize(**kwargs))
        with engine.lock:
            ensure_loaded(engine)
        return (engine,)
