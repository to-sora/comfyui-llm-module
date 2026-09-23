import weakref


class EXLPrefix:
    def __init__(self, backend):
        self.backend = weakref.proxy(backend)
        self.entries = {}
        self.stats = {"hits": 0, "misses": 0, "bytes": 0, "warmed": 0}

    def warm(self):
        import torch
        b = self.backend
        for text in set(b.spec["prefixes"].values()):
            ids = b.encode([{"role": "system", "content": text}], False)
            length = ids.shape[1]
            if length >= b.spec["context_tokens"]:
                raise ValueError("Configured prefix exceeds context_tokens")
            b.kv.current_seq_len = 0
            with torch.inference_mode():
                b.model.forward(ids, b.kv, preprocess_only=True)
            states = [t[:, :length].detach().to("cpu", copy=True)
                      for t in b.kv.key_states + b.kv.value_states]
            size = sum(t.nelement() * t.element_size() for t in states)
            if self.stats["bytes"] + size > b.spec["prefix_cache_mb"] * 1048576:
                raise MemoryError("EXL2 prefixes exceed prefix_cache_mb")
            self.entries[text] = (ids, states)
            self.stats["bytes"] += size
            self.stats["warmed"] += 1
        b.kv.current_seq_len = 0

    def restore(self, prefix):
        b = self.backend
        entry = self.entries.get(prefix)
        if entry is None:
            b.generator.sequence_ids = None
            b.kv.current_seq_len = 0
            self.stats["misses"] += 1
            return
        ids, states = entry
        length = ids.shape[1]
        for target, state in zip(b.kv.key_states + b.kv.value_states, states):
            target[:, :length].copy_(state)
        b.kv.current_seq_len = length
        b.generator.sequence_ids = ids.clone()
        self.stats["hits"] += 1
