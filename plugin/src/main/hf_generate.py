import torch
from .generation_controls import StopGeneration, single_tool, end_tokens
from .cache_stats import describe
from .prefix_context import prepared
from .generation_result import opened, finish


def generate(engine, request, inputs):
    model, cfg, processor = engine.model, engine.cfg, engine.processor
    inputs = inputs.to(model.device)
    count = inputs["input_ids"].shape[-1]
    limit = request.get("max_completion_tokens", request.get("max_tokens", 256))
    if count + limit > cfg["context_tokens"]:
        raise ValueError("Prompt and reply exceed context capacity; shorten the conversation")
    if request.get('diagnostic_prefix'):
        from .prefix_probe import inspect
        inspect(engine, request, inputs)
    temperature = request.get("temperature", 0.0)
    tokenizer = getattr(processor, "tokenizer", processor)
    thinking_open = opened(tokenizer, inputs)
    native_gemma = model.config.model_type == "gemma4"
    marker = "<tool_call|>" if native_gemma else "</tool_call>"
    options = {"do_sample": temperature > 0, "max_new_tokens": limit,
               "use_cache": True,
               **end_tokens(model, tokenizer),
               "stopping_criteria": [StopGeneration(tokenizer, marker if single_tool(request) else None)]}
    if temperature > 0:
        options.update(temperature=temperature, top_p=request.get("top_p", 1.0),
                       top_k=request.get("top_k", 0), min_p=request.get("min_p", 0.0))
    if "seed" in request:
        torch.manual_seed(request["seed"])
    if request.get('diagnostic_scores'):
        from .generation_probe import Scores
        options['logits_processor'] = [Scores(engine, tokenizer)]
    if request.get("stream") and request.get("comfy_prompt_id"):
        from .hf_stream import TokenStream
        options["streamer"] = TokenStream(tokenizer, request, thinking_open)
    with prepared(engine, request, inputs) as cache:
        output = model.generate(**inputs, past_key_values=cache, **options)
    engine.diagnostics["kv"] = describe(cache)
    tokens = output[0, count:]
    return finish(engine, request, tokens, count, thinking_open)
