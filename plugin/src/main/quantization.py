import torch
from transformers import BitsAndBytesConfig


def configuration(name, config):
    if name in {"auto", "none"}:
        return {}
    if getattr(config, "quantization_config", None):
        raise ValueError("Prequantized checkpoint: select auto.")
    if name not in {"bnb_nf4", "bnb_fp4", "bnb_int8"}:
        raise ValueError(f"Unsupported HF weight quantization: {name}")
    quant = BitsAndBytesConfig(
        load_in_4bit=name != "bnb_int8", load_in_8bit=name == "bnb_int8",
        bnb_4bit_quant_type="fp4" if name == "bnb_fp4" else "nf4",
        bnb_4bit_compute_dtype=torch.bfloat16, bnb_4bit_use_double_quant=True)
    return {"quantization_config": quant}
