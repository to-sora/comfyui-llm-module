import torch
import transformers as tr
import psutil
from .quantization import configuration
from .settings import APP
from . import weight_cache
from .estimate import weights
from .offload_budget import weight_budget


def processor(cfg):
    common = {"trust_remote_code": False, "cache_dir": str(APP / "data/hf/hub")}
    config = tr.AutoConfig.from_pretrained(cfg["model"], **common)
    vision = hasattr(config, "vision_config")
    cls = tr.AutoProcessor if vision else tr.AutoTokenizer
    value = cls.from_pretrained(cfg["model"], **common)
    if cfg.get("chat_template"):
        value.chat_template = (APP / cfg["chat_template"]).read_text()
    return value, vision


def load(cfg, proc, vision, budget):
    source = weight_cache.source(cfg)
    common = {"trust_remote_code": False, "cache_dir": str(APP / "data/hf/hub")}
    config = tr.AutoConfig.from_pretrained(source, **common)
    cls = tr.AutoModelForImageTextToText if vision else tr.AutoModelForCausalLM
    dtype = getattr(torch, cfg.get("precision", "bfloat16"))
    device = cfg["device"]
    options = {} if source != cfg["model"] else configuration(cfg["quantization"], config, dtype)
    saved = getattr(config, "quantization_config", {})
    if saved.get("quant_method") == "bitsandbytes":
        quant = tr.BitsAndBytesConfig.from_dict(saved)
        quant.bnb_4bit_compute_dtype = dtype
        options["quantization_config"] = quant
    mapping = {"": device}
    if device != "cpu" and weights(cfg) > budget:
        mapping = "auto"
        options["max_memory"] = {torch.device(device).index or 0: weight_budget(config, budget),
                                 "cpu": int(psutil.virtual_memory().available * .85)}
        quant = options.get("quantization_config")
        if quant:
            quant.llm_int8_enable_fp32_cpu_offload = True
    model = cls.from_pretrained(source, config=config, dtype=dtype, device_map=mapping,
                               attn_implementation="sdpa", **options, **common).eval()
    if "disk" in getattr(model, "hf_device_map", {}).values():
        raise MemoryError("The model requires more RAM than is available")
    weight_cache.save(cfg, model, proc)
    model._llm_weight_source = source
    return model
