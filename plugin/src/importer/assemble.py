import torch
from transformers import AutoConfig, AutoModelForImageTextToText, AutoProcessor
from .vision import convert


def assemble(text_model, tokenizer, base, projector, dtype):
    config = AutoConfig.from_pretrained(base, local_files_only=True)
    config.text_config = text_model.config
    if hasattr(config.text_config, "quantization_config"):
        del config.text_config.quantization_config
    with torch.device("meta"):
        model = AutoModelForImageTextToText.from_config(config, dtype=dtype)
    state = {(k.replace("model.", "model.language_model.", 1) if k.startswith("model.") else k): v
             for k, v in text_model.state_dict().items()}
    state.update(convert(projector, dtype))
    expected = model.state_dict()
    missing, extra = set(expected) - set(state), set(state) - set(expected)
    if missing or extra:
        raise ValueError(f"Import key mismatch: missing={sorted(missing)}, unexpected={sorted(extra)}")
    for key, value in state.items():
        if value.shape != expected[key].shape:
            raise ValueError(f"Import shape mismatch at {key}: {value.shape} vs {expected[key].shape}")
    model.load_state_dict(state, strict=True, assign=True)
    processor = AutoProcessor.from_pretrained(base, local_files_only=True)
    processor.tokenizer = tokenizer
    processor.chat_template = tokenizer.chat_template
    return model, processor, len(state)
