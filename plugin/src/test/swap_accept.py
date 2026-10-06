import json
import sys
import time
from pathlib import Path
from .api_client import execute, request
from .sdxl_graph import graph


def main():
    started = time.monotonic()
    name, kv = sys.argv[1:3] if len(sys.argv) > 2 else ("Qwen3.5-9B", "hqq_8")
    body = {"model": name, "kv_quantization": kv,
            "messages": [{"role": "user", "content": "What is 17 + 25? Reply with only the number."}],
            "max_tokens": 32, "temperature": 0}
    def chat():
        result = request("/v1/chat/completions", body)
        assert result["choices"][0]["message"]["content"].strip() == "42", result
        return request("/llm/status")
    first = chat()
    def load_events(state):
        return sum(e["event"] == "loaded" and e.get("model") == body["model"]
                   for e in state["events"])
    loaded = next(m for m in first["models"] if m["loaded"])
    assert loaded["model"] == body["model"]
    second = chat()
    assert next(m for m in second["models"] if m["loaded"])["loads"] == loaded["loads"]
    prompt_id, outputs = execute(graph(seed=int(time.time())))
    assert outputs["7"]["images"]
    middle = request("/llm/status")
    assert all(not m["loaded"] for m in middle["models"]), middle
    transition = next(e for e in reversed(middle["events"]) if e["event"] == "switch")
    freed = transition["cuda_free_after"] - transition["cuda_free_before"]
    assert freed > loaded["resident_bytes"] * 0.8, transition
    final = chat()
    reloaded = next(m for m in final["models"] if m["loaded"])
    assert load_events(final) > load_events(first), final
    evidence = {"status": "PASS", "model": body["model"], "quantization": loaded["quantization"],
                "kv_quantization": kv, "answer_before_and_after": "42",
                "llm_resident_bytes": loaded["resident_bytes"], "bytes_freed_for_sdxl": freed,
                "sdxl_prompt": prompt_id, "sdxl_image": outputs["7"]["images"][0],
                "loads_before": load_events(first), "loads_after": load_events(final),
                "reused_between_requests": True, "seconds": time.monotonic() - started}
    output = Path(__file__).resolve().parents[3] / "fan-out" / f"swap-{name}-{kv}.json"
    output.write_text(json.dumps(evidence, indent=2))
    print(json.dumps(evidence))


if __name__ == "__main__":
    main()
