import json
from .messages import pil_images


class QwenGenerate:
    CATEGORY = "Qwen/LLM"
    RETURN_TYPES = ("STRING",)
    FUNCTION = "generate"
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "model": ("QWEN_MODEL",),
            "prompt": ("STRING", {"multiline": True, "default": "Hello"}),
            "prefix": ("STRING", {"default": "assistant"}),
            "max_tokens": ("INT", {"default": 128, "min": 1, "max": 32768}),
            "temperature": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 2.0}),
        }, "optional": {"images": ("IMAGE",)}}

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("nan")

    def generate(self, model, prompt, prefix, max_tokens, temperature, images=None):
        text = model.spec["prefixes"].get(prefix, prefix)
        output = model.generate([prompt], text, pil_images(images),
                                max_tokens, temperature)[0]
        return {"ui": {"text": [output]}, "result": (output,)}


class QwenBatch(QwenGenerate):
    def generate(self, model, prompt, prefix, max_tokens, temperature, images=None):
        prompts = json.loads(prompt)
        if not isinstance(prompts, list) or not prompts or any(
                not isinstance(p, str) for p in prompts):
            raise ValueError("Batch prompt must be a JSON array of strings")
        text = model.spec["prefixes"].get(prefix, prefix)
        output = model.generate(prompts, text, pil_images(images),
                                max_tokens, temperature)
        return {"ui": {"text": output},
                "result": (json.dumps(output, ensure_ascii=False),)}
