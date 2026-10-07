from .errors import UserError
import asyncio
from .generation import defaults as generation_defaults


async def discover(comfy):
    names = ("KSampler", "EmptyLatentImage", "LLMModel")
    replies = await asyncio.gather(*(comfy.request("/object_info/" + n) for n in names))
    fields = {n: r[n]["input"]["required"] for n, r in zip(names, replies)}
    caps = await comfy.request("/llm/capabilities")
    defaults, enums = {}, {}
    for group in fields.values():
        for name, spec in group.items():
            if isinstance(spec[0], list):
                enums[name] = spec[0]
                defaults[name] = spec[0][0]
            if len(spec) > 1 and "default" in spec[1]:
                defaults[name] = spec[1]["default"]
    defaults.update(generation_defaults())
    defaults.update(checkpoint=("sd_xl_base_1.0.safetensors"
        if "sd_xl_base_1.0.safetensors" in caps["checkpoints"] else next(iter(caps["checkpoints"]), "")),
        backend="auto", mmproj="", max_tokens=512)
    return {**caps, "defaults": defaults, "enums": enums}


def llm_settings(caps, value):
    result = {k: value.get(k, caps["defaults"].get(k)) for k in (
        "model", "quantization", "kv_quantization", "context_tokens", "backend", "mmproj", "max_tokens")}
    profiles = {p["id"]: p for p in caps["profiles"]}
    backend = result["backend"]
    if backend == "auto":
        backend = profiles.get(result["model"], {}).get("backend", "gguf"
            if str(result["model"]).lower().endswith(".gguf") else "transformers")
    allowed = ["none", "q8_0", "q4_0"] if backend == "gguf" else ["none", "hqq_4", "hqq_8"]
    if result["kv_quantization"] not in allowed:
        raise UserError("KV quantization does not match the selected backend")
    if backend == "gguf" and result["quantization"] not in ("default", "auto", "none"):
        raise UserError("GGUF uses its file's weight quantization")
    if not 128 <= int(result["context_tokens"]) <= 262144:
        raise UserError("Context must be between 128 and 262144")
    result["context_tokens"] = int(result["context_tokens"])
    result["max_tokens"] = int(result["max_tokens"])
    if not 1 <= result["max_tokens"] < result["context_tokens"]:
        raise UserError("Reply tokens must be positive and smaller than context")
    if result["quantization"] not in caps["enums"]["quantization"]:
        raise UserError("Unknown weight quantization")
    return result
