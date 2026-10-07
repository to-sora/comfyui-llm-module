import json
import sys
import numpy as np
from llama_cpp import Llama
from transformers import AutoTokenizer
from ..main.settings import APP

PROMPTS = ["What is 17 + 25? Reply with only the number.",
           "Name the capital of France. Reply with only the city name.",
           "Complete: The opposite of hot is", "用繁體中文說一句早安。"]


def main():
    target = APP / "data/imported" / sys.argv[1]
    info = json.loads((target / "import.json").read_text())
    tokenizer = AutoTokenizer.from_pretrained(target, local_files_only=True)
    model = Llama(model_path=info["source"], n_gpu_layers=-1, n_ctx=512,
                  n_batch=512, n_threads=8, logits_all=True, flash_attn=True, verbose=False)
    values, cases = {}, []
    try:
        for index, text in enumerate(PROMPTS):
            prompt = tokenizer.apply_chat_template([{"role": "user", "content": text}],
                tokenize=False, add_generation_prompt=True, enable_thinking=False)
            ids = model.tokenize(prompt.encode(), add_bos=False, special=True)
            assert ids == tokenizer.encode(prompt, add_special_tokens=False)
            model.reset()
            model.eval(ids)
            generated, logits = [], []
            for _ in range(16):
                scores = model.scores[model.n_tokens - 1].copy()
                token = int(scores.argmax())
                generated.append(token)
                logits.append(scores)
                if token == model.token_eos():
                    break
                model.eval([token])
            values[f"logits_{index}"] = np.array(logits)
            cases.append({"text": text, "prompt_ids": ids, "generated_ids": generated,
                          "output": tokenizer.decode(generated, skip_special_tokens=True)})
            print(text, cases[-1]["output"], flush=True)
        np.savez_compressed(target / "logit-reference.npz", **values)
        (target / "logit-reference.json").write_text(json.dumps({"cases": cases,
            "sampling": "argmax, no penalties", "thresholds": {"top1": .98, "mean_kl": .02, "max_kl": .1}},
            ensure_ascii=False, indent=2))
    finally:
        model.close()


if __name__ == "__main__":
    main()
