from .cache_tree import transfer, byte_size


class TensorPrefix:
    def __init__(self, backend):
        self.backend = backend
        self.entries = {}
        self.stats = {"hits": 0, "misses": 0, "bytes": 0, "warmed": 0}

    def warm(self):
        import torch
        import inspect
        b = self.backend
        for text in set(b.spec["prefixes"].values()):
            if not text or text in self.entries:
                continue
            inputs = b.processor.apply_chat_template(
                [{"role": "system", "content": text}], tokenize=True,
                add_generation_prompt=False, return_dict=True,
                return_tensors="pt", enable_thinking=False)
            ids = tuple(inputs["input_ids"][0].tolist())
            if len(ids) >= b.spec["context_tokens"]:
                raise ValueError("Configured prefix exceeds context_tokens")
            args = {k: v.to(b.spec["device"]) for k, v in inputs.items()}
            if "logits_to_keep" in inspect.signature(b.model.forward).parameters:
                args["logits_to_keep"] = 1
            with torch.inference_mode():
                out = b.model(**args, use_cache=True)
            state = transfer(out.past_key_values, "cpu")
            size = byte_size(state)
            if self.stats["bytes"] + size > b.spec["prefix_cache_mb"] * 1048576:
                raise MemoryError("Startup prefixes exceed prefix_cache_mb")
            self.entries[text] = (ids, state)
            self.stats["bytes"] += size
            self.stats["warmed"] += 1

    def restore(self, inputs, prefix, images):
        b = self.backend
        for module in b.model.modules():
            if hasattr(module, "rope_deltas"):
                module.rope_deltas = None
        entry = self.entries.get(prefix)
        if entry and not images:
            ids, state = entry
            current = tuple(inputs["input_ids"][0, :len(ids)].tolist())
            if current == ids and inputs["input_ids"].shape[1] > len(ids):
                inputs["past_key_values"] = transfer(state, b.spec["device"])
                self.stats["hits"] += 1
                return
        self.stats["misses"] += 1
