import json
import sys
import torch
from transformers import AutoModelForImageTextToText, AutoProcessor
from ..main.settings import APP
from ..main.hf_inputs import prepare
from .vision_cases import messages


def main():
    target = APP / "data/imported" / sys.argv[1]
    reference = json.loads((target / "vision-reference.json").read_text())
    torch.set_num_threads(8)
    processor = AutoProcessor.from_pretrained(target, local_files_only=True)
    model = AutoModelForImageTextToText.from_pretrained(target, dtype=torch.float16,
        device_map="auto", max_memory={0: "18GiB", "cpu": "90GiB"},
        attn_implementation="sdpa", local_files_only=True).eval()
    rows = []
    with torch.inference_mode():
        for case in reference:
            inputs = prepare(processor, True, {"messages": messages(case["image"], case["question"])}, [])
            inputs = inputs.to(model.device)
            out = model.generate(**inputs, do_sample=False, max_new_tokens=24)
            text = processor.decode(out[0, inputs.input_ids.shape[-1]:], skip_special_tokens=True).strip()
            row = {"image": case["image"], "question": case["question"], "reference": case["answer"],
                   "actual": text, "equal": text == case["answer"], "prompt_tokens": int(inputs.input_ids.shape[-1])}
            rows.append(row)
            print(json.dumps(row, ensure_ascii=False), flush=True)
    result = {"status": "PASS" if all(r["equal"] for r in rows) else "FAIL", "cases": rows}
    (target / "vision-parity.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
