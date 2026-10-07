import argparse
import json
from pathlib import Path
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, GgufConfig
from transformers.integrations.gguf import kernels
from ..main.registry import profiles
from ..main.settings import APP, environment
from .assemble import assemble


def main():
    parser = argparse.ArgumentParser(description="Offline GGUF + projector to HF; profiles stay unchanged")
    parser.add_argument("profile")
    parser.add_argument("--base", required=True, help="Matching HF architecture and processor repository")
    parser.add_argument("--precision", choices=("float16", "bfloat16"), default="float16")
    args = parser.parse_args()
    environment()
    torch.set_num_threads(8)
    kernels._gguf_kernel = False
    cfg = profiles()[args.profile]
    source = Path(cfg["model"])
    target = APP / "data/imported" / args.profile
    if target.exists():
        raise FileExistsError(f"Existing import is retained: {target}")
    staging = target.with_name(target.name + ".partial")
    staging.mkdir(parents=True, exist_ok=True)
    tokenizer = AutoTokenizer.from_pretrained(source.parent, gguf_file=source.name, local_files_only=True)
    dtype = getattr(torch, args.precision)
    text, info = AutoModelForCausalLM.from_pretrained(source.parent, gguf_file=source.name,
        quantization_config=GgufConfig(dequantize=True), dtype=dtype, device_map={"": "cpu"},
        local_files_only=True, output_loading_info=True)
    if info.get("missing_keys") or info.get("unexpected_keys") or info.get("mismatched_keys"):
        raise ValueError(f"Text conversion did not load strictly: {info}")
    model, processor, count = assemble(text, tokenizer, args.base, cfg["mmproj"], dtype)
    model.save_pretrained(staging, safe_serialization=True, max_shard_size="2GB")
    processor.save_pretrained(staging)
    evidence = {"profile": args.profile, "source": str(source), "projector": cfg["mmproj"],
        "precision": args.precision, "tensor_count": count, "missing_keys": [], "unexpected_keys": [],
        "shape_mismatches": [], "structure": "PASS", "remaining_gates": ["tokenizer", "template", "logits", "vision", "workflows"]}
    (staging / "import.json").write_text(json.dumps(evidence, indent=2))
    staging.rename(target)
    print(json.dumps(evidence), flush=True)


if __name__ == "__main__":
    main()
