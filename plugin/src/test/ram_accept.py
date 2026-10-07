import json
import time
from pathlib import Path
from .api_client import request, execute
from .sdxl_graph import graph

body = {"model": "Qwen3.5-9B", "kv_quantization": "hqq_8", "max_tokens": 32,
        "messages": [{"role": "user", "content": "What is 17 + 25? Reply with only the number."}]}

def chat():
    reply = request("/v1/chat/completions", body)
    assert reply["choices"][0]["message"]["content"].strip() == "42", reply
    return request("/llm/status")

def model(state):
    return next(m for m in state["models"] if m["model"] == body["model"])

before = chat()
image, _ = execute(graph())
middle = request("/llm/status")
assert model(middle)["loaded"], "The 9B model should remain resident when both models fit"
assert model(middle)["loads"] == model(before)["loads"]
request("/free", {"unload_models": True, "free_memory": True}, binary=True)
for _ in range(60):
    offloaded = request("/llm/status")
    if not model(offloaded)["loaded"]:
        break
    time.sleep(.25)
else:
    raise AssertionError("ComfyUI did not offload the model")
assert model(offloaded)["in_ram"] and model(offloaded)["diagnostics"]["storage"]["cpu"] > 0
final = chat()
assert model(final)["loads"] == model(before)["loads"]
assert model(final)["transfers"] > model(before)["transfers"]
assert not any(e["event"] == "switch" for e in final["events"])
output = Path(__file__).resolve().parents[3] / "fan-out/studio-engine"
output.mkdir(exist_ok=True)
data = {"status": "PASS", "answer": "42", "sdxl_prompt": image,
        "coexists_with_sdxl": True, "models": [{k: model(s)[k] for k in ("model", "loaded", "in_ram", "resident_bytes", "loads", "transfers")}
                   for s in (before, middle, offloaded, final)]}
(output / "ram.json").write_text(json.dumps(data, indent=2))
print("Real 9B+SDXL coexistence, ComfyUI Free→CPU RAM→GPU restore without reload PASS")
