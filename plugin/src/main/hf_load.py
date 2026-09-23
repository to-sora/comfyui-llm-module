def load(cfg):
    import torch
    import transformers as tr
    from .quantization import configuration
    from .settings import APP
    common = {"trust_remote_code": cfg["trust_remote_code"],
              "cache_dir": str(APP / "data/hf/hub")}
    config = tr.AutoConfig.from_pretrained(cfg["model"], **common)
    vision = hasattr(config, "vision_config")
    if vision:
        cls = tr.AutoModelForImageTextToText
        processor = tr.AutoProcessor.from_pretrained(cfg["model"], **common)
    else:
        cls = tr.AutoModelForCausalLM
        processor = tr.AutoTokenizer.from_pretrained(cfg["model"], **common)
    device = cfg["device"]
    if device == "auto":
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
    dtype = torch.float32 if device == "cpu" else torch.float16
    if device.startswith("cuda") and torch.cuda.is_bf16_supported():
        dtype = torch.bfloat16
    model = cls.from_pretrained(
        cfg["model"], config=config, dtype=dtype,
        device_map={"": device}, attn_implementation="sdpa",
        **configuration(cfg["quantization"], config), **common,
    ).eval()
    return model, processor, vision
