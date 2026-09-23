import sys
from .ipv4 import enable
from .settings import environment

enable()
environment()
model = sys.argv[1] if len(sys.argv) > 1 else "Qwen/Qwen3.5-0.8B"
if model.endswith(".gguf"):
    from .gguf_files import resolve
    print(resolve(model))
else:
    from huggingface_hub import snapshot_download
    print(snapshot_download(model, allow_patterns=[
        "*.safetensors", "*.json", "*.txt", "*.model", "*.tiktoken", "*.py"]))
