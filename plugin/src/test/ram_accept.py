import json
import time
import sys
import secrets
from pathlib import Path
from .api_client import request, execute
from .sdxl_graph import graph
from .model_cases import MEMORY_SYSTEM

mode = sys.argv[1] if len(sys.argv) > 1 else "bnb_nf4"
body = {"quantization": mode, "model": "Qwen3.5-9B", "kv_quantization": "hqq_8", "max_tokens": 32,
        "messages": [{"role":"system","content":MEMORY_SYSTEM},
                     {"role": "user", "content": "What is 17 + 25? Reply with only the number."}]}

def chat():
    reply = request("/v1/chat/completions", body)
    assert reply["choices"][0]["message"]["content"].strip() == "42", reply
    return request("/llm/status")

def model(state):
    return next(m for m in state['models'] if m['model']==body['model'] and m['quantization']==mode
                and m['kv_quantization']=='hqq_8' and m['precision']=='bfloat16' and m['context_tokens']==16384)

before = chat()
for _ in range(8):
    repeated = chat()
    assert model(repeated)["registry_entries"] == 1, repeated["managed_models"]
    assert model(repeated)["loads"] == model(before)["loads"]
image, _ = execute(graph(secrets.randbits(52)))
middle = request("/llm/status")
assert model(middle)["loaded"], "Both models fit"
assert model(middle)["loads"] == model(before)["loads"]
request("/free", {"unload_models": True}, binary=True)
for _ in range(60):
    offloaded = request("/llm/status")
    if (not model(offloaded)["loaded"] and model(offloaded)["registry_entries"] == 0
            and offloaded["cuda_free"] > middle["cuda_free"] + model(middle)["resident_bytes"] * .8):
        break
    time.sleep(.25)
else:
    raise AssertionError("Offload timeout")
assert model(offloaded)["diagnostics"]["storage"]["cuda"] == 0, model(offloaded)
assert model(offloaded)["in_ram"] and model(offloaded)["diagnostics"]["storage"]["cpu"] > 0
final = chat()
assert model(final)["loads"] == model(before)["loads"]
assert model(final)["transfers"] > model(before)["transfers"]
assert model(final)["registry_entries"] == 1
assert model(final)['diagnostics']['prefix']['last_reused_tokens'] > 0
assert model(final)["resident_bytes"] <= model(before)["resident_bytes"] * 1.01, model(final)
assert not any(e["event"] == "switch" for e in final["events"])
output = Path(__file__).resolve().parents[3] / "fan-out/studio-engine"
output.mkdir(exist_ok=True)
data = {"status": "PASS", "answer": "42", "sdxl_prompt": image,
        "prefix_after_ram_restore": model(final)['diagnostics']['prefix'],
        "cuda_free_bytes": [s["cuda_free"] for s in (before, middle, offloaded, final)],
        "coexists_with_sdxl": True, "repeated_chat_calls": 9,
        "models": [{k: model(s)[k] for k in ("model", "loaded", "in_ram", "resident_bytes", "loads", "transfers", "registry_entries")}
                   for s in (before, middle, offloaded, final)]}
(output / ("ram.json" if mode == "bnb_nf4" else "ram-"+mode+".json")).write_text(json.dumps(data, indent=2))
print("RAM and prefix PASS")
