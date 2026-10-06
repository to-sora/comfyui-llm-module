from .registry import options
from .runtime import get_handle


class LLMModel:
    CATEGORY = "LLM"
    RETURN_TYPES = ("LLM_MODEL",)
    FUNCTION = "load"
    DESCRIPTION = "Select an HF or GGUF model. ComfyUI loads it when generation begins."

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "model": ("STRING", {"default": "Qwen3.5-9B"}),
            "quantization": (["default", "auto", "none", "bnb_nf4", "bnb_fp4", "bnb_int8"],),
            "kv_quantization": (["none", "hqq_8", "hqq_4", "q8_0", "q4_0"],),
            "context_tokens": ("INT", {"default": 4096, "min": 128, "max": 262144}),
        }, "optional": {
            "backend": (["auto", "transformers", "gguf"],),
            "mmproj": ("STRING", {"default": ""}),
            "device": (["auto", "cuda:0", "cpu"],),
        }}

    def load(self, model, quantization, kv_quantization, context_tokens,
             backend="auto", mmproj="", device="auto"):
        overrides = dict(quantization=quantization, kv_quantization=kv_quantization,
                         context_tokens=context_tokens, mmproj=mmproj, device=device)
        if backend != "auto":
            overrides["backend"] = backend
        return (get_handle(options(model, **overrides)),)
