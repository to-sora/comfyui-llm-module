from functools import lru_cache
import torch
from transformers import AutoConfig, AutoModelForCausalLM, AutoModelForImageTextToText
from .settings import APP


@lru_cache(maxsize=24)
def parameter_counts(source):
    cfg = AutoConfig.from_pretrained(source, trust_remote_code=False,
                                    cache_dir=str(APP / "data/hf/hub"))
    cls = AutoModelForImageTextToText if hasattr(cfg, "vision_config") else AutoModelForCausalLM
    with torch.device("meta"):
        model = cls.from_config(cfg)
    linear = {id(m.weight) for name, m in model.named_modules()
              if isinstance(m, torch.nn.Linear) and not name.endswith("lm_head")}
    total = sum(p.numel() for p in model.parameters())
    packed = sum(p.numel() for p in model.parameters() if id(p) in linear)
    return packed, total-packed
