import re
from pathlib import Path


def resolve(name):
    if "::" not in name:
        path = Path(name).expanduser()
        if not path.is_file():
            raise FileNotFoundError(name)
        return str(path.resolve())
    from huggingface_hub import hf_hub_download
    from .settings import APP
    cache = str(APP / "data/hf/hub")
    repo, filename = name.split("::", 1)
    match = re.search(r"-00001-of-(\d{5})\.gguf$", filename)
    if match:
        for part in range(2, int(match[1]) + 1):
            hf_hub_download(repo, filename.replace("-00001-of-", f"-{part:05}-of-"), cache_dir=cache)
    return hf_hub_download(repo, filename, cache_dir=cache)


def chat_prefix(prefix):
    return f"<|im_start|>system\n{prefix}<|im_end|>\n" if prefix else ""


def image_messages(prefix, prompt, images):
    import base64
    import io
    content = []
    for image in images:
        stream = io.BytesIO()
        image.save(stream, format="PNG")
        url = "data:image/png;base64," + base64.b64encode(stream.getvalue()).decode()
        content.append({"type": "image_url", "image_url": {"url": url}})
    content.append({"type": "text", "text": prompt})
    return [{"role": "system", "content": prefix}, {"role": "user", "content": content}]
