import torch
from .generation_controls import StopGeneration, single_tool
from .cache_stats import describe
from .kv_cache import create
from .tool_calls import parse
from .gemma_tools import parse as parse_gemma
from .model_response import parse as parse_response


def generate(engine, request, inputs):
    model, cfg, processor = engine.model, engine.cfg, engine.processor
    inputs = inputs.to(model.device)
    count = inputs["input_ids"].shape[-1]
    limit = request.get("max_completion_tokens", request.get("max_tokens", 256))
    if count + limit > cfg["context_tokens"]:
        raise ValueError("Prompt and reply exceed context capacity; shorten the conversation")
    temperature = request.get("temperature", 0.0)
    tokenizer = getattr(processor, "tokenizer", processor)
    native_gemma = model.config.model_type == "gemma4"
    marker = "<tool_call|>" if native_gemma else "</tool_call>"
    cache = create(model.config, cfg["kv_quantization"])
    options = {"do_sample": temperature > 0, "max_new_tokens": limit,
               "past_key_values": cache, "use_cache": True,
               "stopping_criteria": [StopGeneration(tokenizer, marker if single_tool(request) else None)]}
    if temperature > 0:
        options.update(temperature=temperature, top_p=request.get("top_p", 1.0),
                       top_k=request.get("top_k", 0), min_p=request.get("min_p", 0.0))
    if "seed" in request:
        torch.manual_seed(request["seed"])
    if request.get("stream") and request.get("comfy_prompt_id"):
        from .hf_stream import TokenStream
        options["streamer"] = TokenStream(tokenizer, request)
    output = model.generate(**inputs, **options)
    engine.diagnostics["kv"] = describe(cache)
    tokens = output[0, count:]
    raw = processor.decode(tokens, skip_special_tokens=False)
    message = parse_response(parse_gemma if native_gemma else parse, raw, request.get("tools"))
    reason = "tool_calls" if message.get("tool_calls") else "length" if len(tokens) >= limit else "stop"
    return {"message": message, "finish_reason": reason,
            "usage": {"prompt_tokens": count, "completion_tokens": len(tokens),
                      "total_tokens": count + len(tokens)}}
