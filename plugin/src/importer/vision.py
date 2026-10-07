import re
import torch
from transformers.integrations.gguf.reader import GgufHeader, load_gguf_state_dict


def convert(path, dtype):
    header = GgufHeader.from_file(str(path))
    if header.architecture != "clip":
        raise ValueError("Expected a Qwen vision projector")
    lazy = load_gguf_state_dict(header)
    result, patches = {}, {}
    leaves = {"attn_out": "attn.proj", "attn_qkv": "attn.qkv", "ffn_up": "mlp.linear_fc1",
              "ffn_down": "mlp.linear_fc2", "ln1": "norm1", "ln2": "norm2"}
    extras = {"mm.0": "merger.linear_fc1", "mm.2": "merger.linear_fc2",
              "v.post_ln": "merger.norm", "v.patch_embd": "patch_embed.proj",
              "v.position_embd": "pos_embed"}
    for name, tensor in lazy.items():
        value = tensor[:].to(dtype)
        if name in ("v.patch_embd.weight", "v.patch_embd.weight.1"):
            patches[name] = value
            continue
        m = re.fullmatch(r"v\.blk\.(\d+)\.([^.]+)\.(weight|bias)", name)
        if m:
            layer, leaf, suffix = m.groups()
            target = f"blocks.{layer}.{leaves[leaf]}.{suffix}"
        else:
            prefix, suffix = name.rsplit(".", 1)
            if prefix not in extras:
                raise ValueError(f"Unmapped projector tensor: {name}")
            target = extras[prefix] + "." + suffix
        result["model.visual." + target] = value
    result["model.visual.patch_embed.proj.weight"] = torch.stack([
        patches["v.patch_embd.weight"], patches["v.patch_embd.weight.1"]], dim=2)
    return result
