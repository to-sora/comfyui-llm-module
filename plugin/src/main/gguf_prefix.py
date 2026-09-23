class GGUFPrefix:
    def __init__(self, model, spec):
        from llama_cpp.llama_chat_format import Jinja2ChatFormatter
        self.entries = {}
        self.stats = {"hits": 0, "misses": 0, "bytes": 0, "warmed": 0}
        template = model.metadata.get("tokenizer.chat_template")
        if not template:
            raise ValueError("GGUF checkpoint requires embedded chat template")
        decode = lambda t: model.detokenize([t]).decode("utf-8", "replace")
        formatter = Jinja2ChatFormatter(template=template,
            eos_token=decode(model.token_eos()), bos_token=decode(model.token_bos()),
            add_generation_prompt=False)
        for prefix in set(spec["prefixes"].values()):
            text = formatter(messages=[{"role": "system", "content": prefix}]).prompt
            ids = model.tokenize(text.encode(), add_bos=False, special=True)
            if len(ids) >= spec["context_tokens"]:
                raise ValueError("Configured prefix exceeds context_tokens")
            model.reset()
            model.eval(ids)
            state = model.save_state()
            size = state.llama_state_size + state.scores.nbytes + state.input_ids.nbytes
            if self.stats["bytes"] + size > spec["prefix_cache_mb"] * 1048576:
                raise MemoryError("GGUF prefix states exceed prefix_cache_mb")
            self.entries[prefix] = state
            self.stats["bytes"] += size
            self.stats["warmed"] += 1
        model.reset()

    def restore(self, model, prefix, images):
        model.reset()
        state = self.entries.get(prefix)
        if state is not None and not images:
            model.load_state(state)
            self.stats["hits"] += 1
        else:
            self.stats["misses"] += 1
