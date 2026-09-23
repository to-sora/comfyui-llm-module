def configuration(name, config):
    import transformers as tr
    existing = getattr(config, "quantization_config", None)
    if name == "auto":
        return {}
    if existing and name != "auto":
        raise ValueError("Prequantized checkpoint: select auto / 預量化模型選擇 auto")
    if name == "none":
        return {}
    if name in {"bnb_nf4", "bnb_fp4", "bnb_int8"}:
        import torch
        quant = tr.BitsAndBytesConfig(
            load_in_4bit=name != "bnb_int8", load_in_8bit=name == "bnb_int8",
            bnb_4bit_quant_type="fp4" if name == "bnb_fp4" else "nf4",
            bnb_4bit_compute_dtype=torch.float16,
        )
    elif name == "hqq_int4":
        quant = tr.HqqConfig(nbits=4, group_size=64)
    elif name == "quanto_int8":
        quant = tr.QuantoConfig(weights="int8")
    else:
        raise ValueError(f"Unknown quantization: {name}")
    return {"quantization_config": quant}
