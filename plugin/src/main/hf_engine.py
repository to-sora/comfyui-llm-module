from .cache import PrefixCache, nbytes, snapshot
from .hf_inputs import prefill_inputs, prepare
from .hf_load import load


class HFEngine:
    def __init__(self, cfg):
        self.cfg = cfg
        self.model, self.processor, self.vision = load(cfg)
        self.cache = PrefixCache(cfg["cache_mib"] * 1024**2 // cfg["workers"])
        self.weight_bytes = sum(p.numel() * p.element_size()
                                for p in self.model.parameters())

    def reset_rope(self):
        core = getattr(self.model, "model", self.model)
        if hasattr(core, "rope_deltas"):
            core.rope_deltas = None

    def warm(self):
        import torch
        with torch.inference_mode():
            for prefix in self.cfg["prefixes"].values():
                if not prefix or not self.cache.budget:
                    continue
                self.reset_rope()
                inputs = prefill_inputs(self, prefix)
                if inputs["input_ids"].shape[-1] >= self.cfg["context_tokens"]:
                    raise ValueError("Prefix exceeds context_tokens")
                state = self.model(**inputs, use_cache=True).past_key_values
                cpu = snapshot(state, "cpu")
                self.cache.put(inputs["input_ids"][0].tolist(), cpu, nbytes(cpu))

    def generate(self, prompt, prefix, images, max_tokens, temperature, prefix_cache=True):
        import torch
        with torch.inference_mode():
            self.reset_rope()
            inputs = prepare(self, prefix, prompt, images)
            count = inputs["input_ids"].shape[-1]
            if count + max_tokens > self.cfg["context_tokens"]:
                raise ValueError("Prompt + output exceeds context_tokens")
            state = None if images or not prefix_cache else self.cache.match(
                inputs["input_ids"][0].tolist())
            extra = {} if state is None else {
                "past_key_values": snapshot(state, self.model.device)}
            if temperature > 0:
                extra["temperature"] = temperature
            output = self.model.generate(
                **inputs, **extra, max_new_tokens=max_tokens,
                do_sample=temperature > 0, use_cache=True,
            )
            text = self.processor.decode(output[0, count:], skip_special_tokens=True)
            return text

    def close(self):
        self.model = self.processor = None
        self.cache.entries.clear()
        self.cache.bytes = 0
