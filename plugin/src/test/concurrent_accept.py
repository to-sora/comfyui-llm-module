import json
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from .api_client import request, execute
from .model_cases import user, image_message
from .sdxl_graph import graph


def main():
    started = time.monotonic()
    cases = [(user("What is 19 + 24? Reply with only the number."), "43"),
             (image_message("green"), "green"),
             (user("What is 8 times 7? Reply with only the number."), "56"),
             (image_message("yellow"), "yellow")]
    def chat(case):
        message, expected = case
        result = request("/v1/chat/completions", {"model": "Qwen3.5-9B",
            "kv_quantization": "hqq_4", "max_tokens": 32, "messages": [message]})
        answer = result["choices"][0]["message"]["content"].strip().lower()
        assert expected in answer, (expected, answer)
        return {"expected": expected, "actual": answer}
    with ThreadPoolExecutor(max_workers=5) as pool:
        futures = [pool.submit(chat, case) for case in cases]
        image = pool.submit(execute, graph(seed=int(time.time())))
        answers = [future.result() for future in futures]
        prompt, outputs = image.result()
    assert outputs["7"]["images"]
    state = request("/llm/status")
    proof = {"status": "PASS", "concurrent_requests": 5, "answers": answers,
             "sdxl_prompt": prompt, "sdxl_image": outputs["7"]["images"][0],
             "managed_models": state["managed_models"], "seconds": time.monotonic() - started}
    path = Path(__file__).resolve().parents[3] / "fan-out/concurrency.json"
    path.write_text(json.dumps(proof, indent=2))
    print(json.dumps(proof))


if __name__ == "__main__":
    main()
