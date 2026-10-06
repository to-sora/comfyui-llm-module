import json
from .protocol import response


class LLMChat:
    CATEGORY = "LLM"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("response_json", "text")
    FUNCTION = "generate"
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "model": ("LLM_MODEL",),
            "messages": ("STRING", {"multiline": True,
                "default": '[{"role":"user","content":"What is 2 + 2?"}]'}),
            "max_tokens": ("INT", {"default": 256, "min": 1, "max": 32768}),
            "temperature": ("FLOAT", {"default": 0, "min": 0, "max": 2}),
        }, "optional": {
            "tools": ("STRING", {"default": "[]", "multiline": True}),
            "images": ("IMAGE",),
            "request_json": ("STRING", {"default": "{}"}),
        }}

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("nan")

    def generate(self, model, messages, max_tokens, temperature,
                 tools="[]", images=None, request_json="{}"):
        req = dict(messages=json.loads(messages), tools=json.loads(tools),
                   max_tokens=max_tokens, temperature=temperature)
        req.update(json.loads(request_json))
        result = response(model.cfg["id"], model.chat(req, images))
        encoded = json.dumps(result, ensure_ascii=False)
        text = result["choices"][0]["message"].get("content") or ""
        return {"ui": {"text": [encoded]}, "result": (encoded, text)}
