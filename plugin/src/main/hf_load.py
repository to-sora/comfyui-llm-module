from pathlib import Path
import torch
import transformers as tr
from .quantization import configuration
from .settings import APP


def load(cfg):
    common = {"trust_remote_code": False, "cache_dir": str(APP / "data/hf/hub")}
    config = tr.AutoConfig.from_pretrained(cfg["model"], **common)
    vision = hasattr(config, "vision_config")
    cls = tr.AutoModelForImageTextToText if vision else tr.AutoModelForCausalLM
    processor_cls = tr.AutoProcessor if vision else tr.AutoTokenizer
    processor = processor_cls.from_pretrained(cfg["model"], **common)
    if cfg["chat_template"]:
        processor.chat_template = Path(cfg["chat_template"]).read_text()
    dtype = torch.float32 if cfg["device"] == "cpu" else torch.bfloat16
    model = cls.from_pretrained(
        cfg["model"], config=config, dtype=dtype,
        device_map={"": cfg["device"]}, attn_implementation="sdpa",
        **configuration(cfg["quantization"], config), **common).eval()
    return model, processor, vision
