from pathlib import Path
from .gguf_files import resolve
from .messages import llama_messages


class GGUFBackend:
    def __init__(self, spec):
        self.spec = spec
        self.model = None
        self.size = 0
        self.cache = None

    def load(self):
        if self.model is not None:
            return
        from llama_cpp import Llama
        from llama_cpp.llama_chat_format import MTMDChatHandler
        path = resolve(self.spec, "gguf_file")
        if path is None:
            raise ValueError("GGUF backend requires gguf_file")
        projector = resolve(self.spec, "mmproj_file")
        handler = MTMDChatHandler(projector, verbose=False,
            use_gpu=self.spec["device"] != "cpu") if projector else None
        self.model = Llama(model_path=path,
            n_ctx=self.spec["context_tokens"],
            n_gpu_layers=-1 if self.spec["device"] != "cpu" else 0,
            chat_handler=handler, verbose=False)
        self.size = Path(path).stat().st_size
        if projector:
            self.size += Path(projector).stat().st_size
        from .gguf_prefix import warm
        self.cache = warm(self.model, self.spec)

    def generate(self, prompt, prefix, images, tokens, temperature):
        from .interrupt import check_interrupt
        if images and not self.spec.get("mmproj_file"):
            raise ValueError("GGUF vision requires its matching mmproj_file")
        pieces = []
        stream = self.model.create_chat_completion(
            messages=llama_messages(prefix, prompt, images),
            max_tokens=tokens, temperature=temperature, stream=True)
        try:
            for item in stream:
                check_interrupt()
                pieces.append(item["choices"][0]["delta"].get("content") or "")
        finally:
            stream.close()
        return "".join(pieces)

    def offload(self):
        if self.model:
            self.model.close()
            self.model = None
            self.cache = None
