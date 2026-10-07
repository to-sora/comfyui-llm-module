from .registry import options
from .runtime import get_handle


class LLMModel:
    CATEGORY = "LLM"
    RETURN_TYPES = ("LLM_MODEL",)
    FUNCTION = "load"
    DESCRIPTION = "Select an HF model or a validated GGUF import. ComfyUI manages its memory."

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "model": ("STRING", {"default": "Qwen3.5-9B"}),
            "quantization": (["default", "auto", "none", "bnb_nf4", "bnb_fp4", "bnb_int8"],),
            "kv_quantization": (["none", "hqq_8", "hqq_4"],),
            "context_tokens": ("INT", {"default": 16384, "min": 128, "max": 262144}),
        }, "optional": {
            "backend": (["auto", "transformers"],),
            "device": (["auto", "cuda:0", "cpu"],),
            "precision": (["bfloat16", "float16"],),
        }}

    def load(self, model, quantization, kv_quantization, context_tokens,
             backend="auto", mmproj="", device="auto", precision="bfloat16"):
        overrides = dict(quantization=quantization, kv_quantization=kv_quantization,
                         context_tokens=context_tokens, mmproj=mmproj, device=device, precision=precision)
        if backend != "auto":
            overrides["backend"] = backend
        return (get_handle(options(model, **overrides)),)
