from pathlib import Path
from .cache import PrefixCache
from .gguf_files import chat_prefix, image_messages, resolve


class GGUFEngine:
    def __init__(self, cfg):
        import torch
        from llama_cpp import Llama
        self.cfg = cfg
        handler = None
        gpu = cfg["device"] != "cpu" and torch.cuda.is_available()
        if cfg["mmproj"]:
            from llama_cpp.llama_chat_format import MTMDChatHandler
            handler = MTMDChatHandler(resolve(cfg["mmproj"]), use_gpu=gpu)
        path = resolve(cfg["model"])
        self.model = Llama(model_path=path, n_ctx=cfg["context_tokens"],
                           n_gpu_layers=-1 if gpu else 0, chat_handler=handler,
                           logits_all=False, verbose=False)
        self.weight_bytes = Path(path).stat().st_size
        self.cache = PrefixCache(cfg["cache_mib"] * 1024**2 // cfg["workers"])

    def warm(self):
        for prefix in self.cfg["prefixes"].values():
            if not prefix or not self.cache.budget:
                continue
            tokens = self.model.tokenize(chat_prefix(prefix).encode(), special=True)
            if len(tokens) >= self.cfg["context_tokens"]:
                raise ValueError("Prefix exceeds context_tokens")
            self.model.reset()
            self.model.eval(tokens)
            state = self.model.save_state()
            size = state.llama_state_size + state.scores.nbytes + state.input_ids.nbytes
            self.cache.put(tokens, state, size)
        self.model.reset()

    def generate(self, prompt, prefix, images, max_tokens, temperature, prefix_cache=True):
        args = dict(max_tokens=max_tokens, temperature=temperature)
        if images:
            if not self.cfg["mmproj"]:
                raise ValueError("GGUF vision requires mmproj / GGUF 視覺需要 mmproj")
            result = self.model.create_chat_completion(
                messages=image_messages(prefix, prompt, images), **args)
            return result["choices"][0]["message"]["content"]
        text = chat_prefix(prefix) + f"<|im_start|>user\n{prompt}<|im_end|>\n"
        text += "<|im_start|>assistant\n"
        tokens = self.model.tokenize(text.encode(), special=True)
        if len(tokens) + max_tokens > self.cfg["context_tokens"]:
            raise ValueError("Prompt + output exceeds context_tokens")
        state = self.cache.match(tokens) if prefix_cache else None
        self.model.reset()
        if state is not None:
            self.model.load_state(state)
        return self.model.create_completion(tokens, stop=["<|im_end|>"], **args)["choices"][0]["text"]

    def close(self):
        self.model.close()
        self.cache.entries.clear()
        self.cache.bytes = 0
