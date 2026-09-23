from .runtime import get_handle
from .settings import options


class QwenModel:
    CATEGORY = "Qwen"
    RETURN_TYPES = ("QWEN_MODEL",)
    FUNCTION = "load"

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "model": ("STRING", {"default": "Qwen/Qwen3.5-0.8B"}),
            "backend": (["auto", "transformers", "gguf"],),
            "quantization": (["auto", "none", "bnb_nf4", "bnb_fp4", "bnb_int8",
                              "hqq_int4", "quanto_int8"],),
            "device": (["auto", "cuda:0", "cpu"],),
            "mode": (["single", "concurrent"],),
        }, "optional": {
            "mmproj": ("STRING", {"default": ""}),
            "trust_remote_code": ("BOOLEAN", {"default": False}),
        }}

    def load(self, model, backend, quantization, device, mode,
             mmproj="", trust_remote_code=False):
        handle = get_handle(options(model, backend, quantization, device, mode,
                                    mmproj, trust_remote_code))
        with handle.pool.lease(handle.ensure):
            pass
        return (handle,)
