def warm(model, spec):
    from llama_cpp import LlamaRAMCache
    from llama_cpp.llama_chat_format import Jinja2ChatFormatter

    class Cache(LlamaRAMCache):
        def __init__(self):
            super().__init__(capacity_bytes=int(spec["prefix_cache_mb"] * 1048576))
            self.stats = {"hits": 0, "misses": 0, "bytes": 0, "warmed": 0}

        def __getitem__(self, key):
            try:
                result = super().__getitem__(key)
                self.stats["hits"] += 1
                return result
            except KeyError:
                self.stats["misses"] += 1
                raise

    cache = Cache()
    model.set_cache(cache)
    template = model.metadata.get("tokenizer.chat_template")
    if not template:
        raise ValueError("GGUF checkpoint requires embedded chat template")
    decode = lambda token: model.detokenize([token]).decode("utf-8", "replace")
    formatter = Jinja2ChatFormatter(template=template,
        eos_token=decode(model.token_eos()), bos_token=decode(model.token_bos()),
        add_generation_prompt=False)
    for prefix in set(spec["prefixes"].values()):
        formatted = formatter(messages=[{"role": "system", "content": prefix}])
        ids = model.tokenize(formatted.prompt.encode(), add_bos=False, special=True)
        if len(ids) >= spec["context_tokens"]:
            raise ValueError("Configured prefix exceeds context_tokens")
        model.reset()
        model.eval(ids)
        state = model.save_state()
        if cache.cache_size + state.llama_state_size > cache.capacity_bytes:
            raise MemoryError("GGUF prefix states exceed prefix_cache_mb")
        cache[tuple(ids)] = state
        cache.stats["warmed"] += 1
    cache.stats["bytes"] = cache.cache_size
    model.reset()
    return cache
