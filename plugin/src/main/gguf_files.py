from pathlib import Path


def resolve(spec, key):
    value = spec.get(key, "")
    if not value:
        return None
    source = Path(spec["model"]).expanduser()
    if source.is_file():
        return str(source if key == "gguf_file" else source.parent / value)
    if source.is_dir():
        return str(source / value)
    from huggingface_hub import hf_hub_download
    from .settings import DATA
    return hf_hub_download(spec["model"], filename=value,
                           cache_dir=str(DATA / "hf"))
