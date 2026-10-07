import json
import sys
import numpy as np
import torch
from transformers import AutoModelForImageTextToText, AutoTokenizer
from ..main.settings import APP


def main():
    target = APP / "data/imported" / sys.argv[1]
    reference = json.loads((target / "logit-reference.json").read_text())
    archive = np.load(target / "logit-reference.npz")
    dtype = sys.argv[2] if len(sys.argv) > 2 else "float16"
    torch.set_num_threads(8)
    model, loading = AutoModelForImageTextToText.from_pretrained(target,
        dtype=getattr(torch, dtype), device_map="auto", max_memory={0: "18GiB", "cpu": "90GiB"},
        attn_implementation="sdpa", local_files_only=True, output_loading_info=True)
    assert not any(loading.get(k) for k in ("missing_keys", "unexpected_keys", "mismatched_keys")), loading
    tokenizer = AutoTokenizer.from_pretrained(target, local_files_only=True)
    rows = []
    with torch.inference_mode():
        for index, case in enumerate(reference["cases"]):
            prompt, expected = case["prompt_ids"], case["generated_ids"]
            inputs = torch.tensor([prompt + expected[:-1]], device=model.device)
            actual = model(inputs, use_cache=False).logits[0, len(prompt)-1:].float().cpu()
            wanted = torch.from_numpy(archive[f"logits_{index}"])
            lp, lq = wanted.log_softmax(-1), actual.log_softmax(-1)
            kl = (lp.exp() * (lp-lq)).sum(-1)
            ids = model.generate(torch.tensor([prompt], device=model.device),
                max_new_tokens=len(expected), do_sample=False)[0, len(prompt):].tolist()
            row = {"prompt": case["text"], "top1": float((actual.argmax(-1) == wanted.argmax(-1)).float().mean()),
                   "mean_kl": float(kl.mean()), "max_kl": float(kl.max()), "greedy_equal": ids == expected,
                   "reference": case["output"], "actual": tokenizer.decode(ids, skip_special_tokens=True)}
            rows.append(row)
            print(json.dumps(row, ensure_ascii=False), flush=True)
    limits = reference["thresholds"]
    passed = all(r["top1"] >= limits["top1"] and r["mean_kl"] <= limits["mean_kl"]
        and r["max_kl"] <= limits["max_kl"] and r["greedy_equal"] for r in rows)
    result = {"profile": sys.argv[1], "precision": dtype, "strict_load": "PASS", "cases": rows,
              "status": "PASS" if passed else "FAIL", "thresholds": limits}
    (target / ("logit-parity-" + dtype + ".json")).write_text(json.dumps(result, ensure_ascii=False, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
