from .errors import UserError


def validate(body):
    choices = {
        "backend": ("auto", "transformers"),
        "quantization": ("default", "auto", "none", "bnb_nf4", "bnb_fp4", "bnb_int8"),
        "kv_quantization": ("none", "hqq_4", "hqq_8"),
        "precision": ("bfloat16", "float16"),
    }
    for key, allowed in choices.items():
        if key in body and body[key] not in allowed:
            raise UserError(f"{key} must be one of: {', '.join(allowed)}")
    if body["model"].lower().endswith(".gguf"):
        raise UserError("Import GGUF into a validated HF repository before serving it")
    size = body.get("context_tokens", 16384)
    if type(size) is not int or not 128 <= size <= 262144:
        raise UserError("context_tokens must be an integer between 128 and 262144")
    if body.get("max_completion_tokens", body.get("max_tokens", 256)) >= size:
        raise UserError("Reply length must be smaller than context_tokens")
