from pathlib import Path


def load(spec):
    import torch
    import transformers as tf
    from .settings import DATA

    source = spec["model"]
    common = {"trust_remote_code": spec["trust_remote_code"],
              "cache_dir": str(DATA / "hf")}
    cfg = tf.AutoConfig.from_pretrained(source, **common)
    vision = hasattr(cfg, "vision_config")
    model_type = getattr(cfg, "model_type", "")
    if "qwen" not in model_type.lower():
        raise ValueError(f"Expected a Qwen architecture, received {model_type}")
    if vision:
        factory = getattr(tf, "AutoModelForMultimodalLM", None)
        factory = factory or tf.AutoModelForImageTextToText
        processor = tf.AutoProcessor.from_pretrained(source, **common)
    else:
        factory = tf.AutoModelForCausalLM
        processor = tf.AutoTokenizer.from_pretrained(source, **common)
    device = spec["device"]
    dtype = spec["dtype"]
    if dtype == "auto":
        dtype = "float32" if device == "cpu" else "float16"
    kwargs = dict(common, config=cfg, dtype=getattr(torch, dtype),
                  device_map={"": device}, attn_implementation="sdpa")
    quant = spec["quantization"]
    if quant != "auto":
        if getattr(cfg, "quantization_config", None):
            raise ValueError("Prequantized weights require quantization=auto")
        kwargs["quantization_config"] = tf.BitsAndBytesConfig(
            load_in_8bit=quant == "int8", load_in_4bit=quant != "int8",
            bnb_4bit_quant_type="nf4" if quant == "nf4" else "fp4",
            bnb_4bit_compute_dtype=getattr(torch, dtype))
    model = factory.from_pretrained(source, **kwargs).eval()
    return model, processor, vision


def weight_bytes(model):
    return sum(p.nelement() * p.element_size() for p in model.parameters())
