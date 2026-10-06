import torch
from .generation_controls import StopGeneration, single_tool
from .cache_stats import describe
from .hf_inputs import prepare
from .hf_load import load
from .images import tensor_images
from .kv_cache import create
from .tool_calls import parse
from .gemma_tools import parse as parse_gemma
from . import gemma_base


class HFEngine:
    def __init__(self, cfg):
        self.cfg = cfg
        self.model, self.processor, self.vision = load(cfg)
        self.diagnostics = {"weight_modules": sum(type(m).__name__ in {"Linear4bit", "Linear8bitLt"}
                                                 for m in self.model.modules())}

    def chat(self, request, images=None):
        inputs = prepare(self.processor, self.vision, request, tensor_images(images))
        inputs = inputs.to(self.model.device)
        count = inputs["input_ids"].shape[-1]
        limit = request.get("max_completion_tokens", request.get("max_tokens", 256))
        if count + limit > self.cfg["context_tokens"]:
            raise ValueError("Prompt and max_tokens exceed configured context_tokens.")
        temperature = request.get("temperature", 0.0)
        tokenizer = getattr(self.processor, "tokenizer", self.processor)
        base = self.cfg.get("base_completion", False)
        native_gemma = self.model.config.model_type == "gemma4" and not base
        marker = "<tool_call|>" if native_gemma else "</tool_call>"
        options = {"do_sample": temperature > 0, "max_new_tokens": limit,
                   "past_key_values": create(self.model.config, self.cfg["kv_quantization"]),
                   "stopping_criteria": [StopGeneration(tokenizer, marker if single_tool(request) else None)],
                   "use_cache": True}
        if base:
            options["stopping_criteria"].append(gemma_base.stopping(tokenizer))
        if temperature > 0:
            options.update(temperature=temperature, top_p=request.get("top_p", 1.0))
        if "seed" in request:
            torch.manual_seed(request["seed"])
        output = self.model.generate(**inputs, **options)
        self.diagnostics["kv"] = describe(options["past_key_values"])
        tokens = output[0, count:]
        raw = self.processor.decode(tokens, skip_special_tokens=False)
        parser = parse_gemma if native_gemma else parse
        message = gemma_base.response(raw, request) if base else parser(raw, request.get("tools"))
        reason = "tool_calls" if message.get("tool_calls") else "length" if len(tokens) >= limit else "stop"
        return {"message": message, "finish_reason": reason,
                "usage": {"prompt_tokens": count, "completion_tokens": len(tokens),
                          "total_tokens": count + len(tokens)}}

    def close(self):
        self.model = self.processor = None
