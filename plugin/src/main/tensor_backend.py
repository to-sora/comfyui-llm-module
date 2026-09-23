from .messages import messages
from .tensor_loader import load, weight_bytes


class TensorBackend:
    def __init__(self, spec):
        self.spec = spec
        self.model = None
        self.size = 0
        self.cache = None

    def load(self):
        if self.model is None:
            self.model, self.processor, self.vision = load(self.spec)
            self.size = weight_bytes(self.model)
        else:
            self.model.to(self.spec["device"])
        from .tensor_prefix import TensorPrefix
        if self.cache is None:
            self.cache = TensorPrefix(self)
        self.cache.warm()

    def encode(self, items):
        kwargs = dict(tokenize=True, return_tensors="pt", return_dict=True,
                      add_generation_prompt=True, enable_thinking=False)
        return self.processor.apply_chat_template(items, **kwargs)

    def generate(self, prompt, prefix, images, tokens, temperature):
        import torch
        from .interrupt import interrupt_criterion
        if images and not self.vision:
            raise ValueError("Images require a vision-language checkpoint")
        inputs = self.encode(messages(prefix, prompt, images))
        length = inputs["input_ids"].shape[1]
        if length + tokens > self.spec["context_tokens"]:
            raise ValueError("Prompt plus output exceeds context_tokens")
        inputs = {k: v.to(self.spec["device"]) for k, v in inputs.items()}
        self.cache.restore(inputs, prefix, bool(images))
        args = dict(max_new_tokens=tokens, do_sample=temperature > 0,
                    stopping_criteria=interrupt_criterion())
        if temperature > 0:
            args["temperature"] = temperature
        with torch.inference_mode():
            output = self.model.generate(**inputs, **args)
        return self.processor.decode(output[0, length:], skip_special_tokens=True)

    def offload(self):
        if self.model is None:
            return
        if getattr(self.model, "hf_quantizer", None):
            self.model = None
            self.cache = None
        else:
            self.model.to("cpu")
            for module in self.model.modules():
                if hasattr(module, "rope_deltas"):
                    module.rope_deltas = None
