from pathlib import Path
from .messages import messages


class EXLBackend:
    def __init__(self, spec):
        self.spec, self.model, self.cache, self.size = spec, None, None, 0

    def load(self):
        if self.model is not None:
            return
        if self.spec["device"] != "cuda:0":
            raise ValueError("EXL2 backend requires cuda:0")
        from exllamav2 import ExLlamaV2, ExLlamaV2Config, ExLlamaV2Cache, ExLlamaV2Tokenizer
        from exllamav2.generator import ExLlamaV2StreamingGenerator
        from transformers import AutoTokenizer
        from huggingface_hub import snapshot_download
        from .settings import DATA
        source = self.spec["model"]
        path = source if Path(source).is_dir() else snapshot_download(source,
            cache_dir=str(DATA / "hf"),
            allow_patterns=["*.json", "*.safetensors", "*.model", "*.jinja"])
        config = ExLlamaV2Config()
        config.model_dir = path
        config.prepare()
        config.max_seq_len = self.spec["context_tokens"]
        self.model = ExLlamaV2(config)
        self.model.load()
        self.kv = ExLlamaV2Cache(self.model)
        self.tokenizer = ExLlamaV2Tokenizer(config)
        self.formatter = AutoTokenizer.from_pretrained(path)
        self.generator = ExLlamaV2StreamingGenerator(self.model, self.kv, self.tokenizer)
        self.size = sum(p.stat().st_size for p in Path(path).glob("*.safetensors"))
        from .exl_prefix import EXLPrefix
        self.cache = EXLPrefix(self)
        self.cache.warm()

    def encode(self, items, generation=True):
        text = self.formatter.apply_chat_template(items, tokenize=False,
            add_generation_prompt=generation, enable_thinking=False)
        return self.tokenizer.encode(text, encode_special_tokens=True)

    def generate(self, prompt, prefix, images, tokens, temperature):
        from exllamav2.generator import ExLlamaV2Sampler
        from .interrupt import check_interrupt
        if images:
            raise ValueError("EXL2 image inputs require a vision adapter")
        ids = self.encode(messages(prefix, prompt))
        if ids.shape[1] + tokens > self.spec["context_tokens"]:
            raise ValueError("Prompt plus output exceeds context_tokens")
        self.cache.restore(prefix)
        settings = ExLlamaV2Sampler.Settings()
        settings.temperature = max(temperature, 0.001)
        if temperature == 0:
            settings.top_k = 1
        self.generator.begin_stream_ex(ids, settings)
        result = []
        for _ in range(tokens):
            check_interrupt()
            chunk = self.generator.stream_ex()
            result.append(chunk["chunk"])
            if chunk["eos"]:
                break
        return "".join(result)

    def offload(self):
        self.cache = None
        self.generator = None
        self.kv = None
        if self.model:
            self.model.unload()
            self.model = None
