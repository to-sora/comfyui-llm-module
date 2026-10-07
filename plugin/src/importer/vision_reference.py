import json
import sys
from llama_cpp import Llama
from llama_cpp.llama_chat_format import MTMDChatHandler
from ..main.settings import APP
from .vision_cases import CASES, messages


def main():
    target = APP / "data/imported" / sys.argv[1]
    info = json.loads((target / "import.json").read_text())
    handler = MTMDChatHandler(info["projector"], verbose=False)
    model = Llama(model_path=info["source"], n_gpu_layers=-1, n_ctx=2048,
                  n_batch=512, n_threads=8, flash_attn=True, verbose=False, chat_handler=handler)
    results = []
    try:
        for file, question in CASES:
            model.reset()
            reply = handler(llama=model, messages=messages(file, question), temperature=0,
                top_k=0, min_p=0, top_p=1, repeat_penalty=1, max_tokens=24, enable_thinking=False)
            row = {"image": file, "question": question,
                   "answer": reply["choices"][0]["message"]["content"].strip(), "usage": reply["usage"]}
            results.append(row)
            print(json.dumps(row, ensure_ascii=False), flush=True)
        (target / "vision-reference.json").write_text(json.dumps(results, ensure_ascii=False, indent=2))
    finally:
        model.close()


if __name__ == "__main__":
    main()
