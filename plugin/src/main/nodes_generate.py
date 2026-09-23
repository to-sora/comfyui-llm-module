import json
from concurrent.futures import ThreadPoolExecutor


class QwenGenerate:
    CATEGORY = "Qwen"
    RETURN_TYPES = ("STRING",)
    FUNCTION = "generate"
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "model": ("QWEN_MODEL",),
            "prompt": ("STRING", {"multiline": True, "default": "Explain prefix caching."}),
            "prefix": ("STRING", {"default": "assistant"}),
            "max_tokens": ("INT", {"default": 128, "min": 1, "max": 32768}),
            "temperature": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 2.0}),
        }, "optional": {"images": ("IMAGE",),
                        "prefix_cache": ("BOOLEAN", {"default": True})}}

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("nan")

    def generate(self, model, prompt, prefix, max_tokens, temperature, images=None, prefix_cache=True):
        pil = None
        if images is not None:
            from PIL import Image
            pil = [Image.fromarray((i.detach().cpu().clamp(0, 1).numpy() * 255)
                                  .astype("uint8")) for i in images]
        text = model.generate(prompt, prefix, pil, max_tokens, temperature, prefix_cache)
        return {"ui": {"text": [text]}, "result": (text,)}


class QwenBatch(QwenGenerate):
    @classmethod
    def INPUT_TYPES(cls):
        data = super().INPUT_TYPES()
        data["required"]["prompt"] = ("STRING", {
            "multiline": True, "default": '["Name a color.", "Name a shape."]'})
        return data

    def generate(self, model, prompt, prefix, max_tokens, temperature, images=None, prefix_cache=True):
        prompts = json.loads(prompt)
        if not isinstance(prompts, list) or not prompts or not all(
                isinstance(p, str) for p in prompts):
            raise ValueError("Batch prompt requires a JSON string array")
        if len(prompts) > model.cfg["queue_limit"]:
            raise ValueError("Batch exceeds queue_limit")
        def run(item):
            return super(QwenBatch, self).generate(
                model, item, prefix, max_tokens, temperature, images, prefix_cache)["result"][0]
        with ThreadPoolExecutor(max_workers=model.cfg["workers"]) as executor:
            output = list(executor.map(run, prompts))
        text = json.dumps(output, ensure_ascii=False)
        return {"ui": {"text": output}, "result": (text,)}
