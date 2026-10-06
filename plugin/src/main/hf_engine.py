import torch
from comfy import model_management as mm
from transformers import StoppingCriteria
from .hf_inputs import prepare
from .hf_load import load
from .images import tensor_images
from .kv_cache import create
from .tool_calls import parse


class Interrupted(StoppingCriteria):
    def __call__(self, input_ids, scores, **kwargs):
        mm.throw_exception_if_processing_interrupted()
        return False


class HFEngine:
    def __init__(self, cfg):
        self.cfg = cfg
        self.model, self.processor, self.vision = load(cfg)

    def chat(self, request, images=None):
        inputs = prepare(self.processor, self.vision, request, tensor_images(images))
        inputs = inputs.to(self.model.device)
        count = inputs["input_ids"].shape[-1]
        limit = request.get("max_completion_tokens", request.get("max_tokens", 256))
        if count + limit > self.cfg["context_tokens"]:
            raise ValueError("Prompt and max_tokens exceed configured context_tokens.")
        temperature = request.get("temperature", 0.0)
        options = {"do_sample": temperature > 0, "max_new_tokens": limit,
                   "past_key_values": create(self.model.config, self.cfg["kv_quantization"]),
                   "stopping_criteria": [Interrupted()], "use_cache": True}
        if temperature > 0:
            options.update(temperature=temperature, top_p=request.get("top_p", 1.0))
        if "seed" in request:
            torch.manual_seed(request["seed"])
        output = self.model.generate(**inputs, **options)
        tokens = output[0, count:]
        raw = self.processor.decode(tokens, skip_special_tokens=False)
        message = parse(raw, request.get("tools"))
        reason = "tool_calls" if message.get("tool_calls") else "length" if len(tokens) >= limit else "stop"
        return {"message": message, "finish_reason": reason,
                "usage": {"prompt_tokens": count, "completion_tokens": len(tokens),
                          "total_tokens": count + len(tokens)}}

    def close(self):
        self.model = self.processor = None
