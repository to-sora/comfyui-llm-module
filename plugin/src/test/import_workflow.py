import json
import sys
import time
from pathlib import Path
from .api_client import request, execute
from .model_cases import TOOL, user, image_message
from .sdxl_graph import graph

profile, mode = sys.argv[1:3]
target = Path(__file__).resolve().parents[2] / "data/imported" / profile
outdir = target
if Path(profile).is_absolute():
    target = Path(profile)
    outdir = Path(__file__).resolve().parents[2] / "data/workflows" / target.name
    outdir.mkdir(parents=True, exist_ok=True)
base = {"model": str(target), "quantization": "none" if mode == "float16" else mode,
        "precision": "float16" if mode == "float16" else "bfloat16",
        "kv_quantization": "none" if mode == "float16" else "hqq_8", "context_tokens": 16384,
        "max_tokens": 96, "temperature": 0, "parallel_tool_calls": False}
started = time.monotonic()


from .model_flow import Flow
flow = Flow(base)
chat, status = flow.chat, flow.status


question = [user("What is 17 + 25? Reply with only the number.")]
answer = chat(question)["content"]
assert answer.strip() == "42", answer
color = chat([image_message("blue")])["content"]
assert "blue" in color.lower(), color
tool_prompt = user("Use get_weather for Hong Kong.")
assistant = chat([tool_prompt], tools=[TOOL])
call = assistant["tool_calls"][0]
assert call["function"]["name"] == "get_weather"
assert json.loads(call["function"]["arguments"])["city"] == "Hong Kong"
tool_reply = chat([tool_prompt, assistant, {"role": "tool", "tool_call_id": call["id"],
    "content": '{"temperature_c":28}'}, user("Reply with only the temperature in Celsius.")], tools=[TOOL])
assert "28" in tool_reply["content"], tool_reply
before = status()
if mode == "float16":
    expected_bytes = json.loads((target / "model.safetensors.index.json").read_text())["metadata"]["total_size"]
    assert sum(before["diagnostics"]["storage"].values()) >= expected_bytes * .99, before
prompt, _ = execute(graph())
during = status()
after_answer = chat(question)["content"]
after = status()
assert after_answer.strip() == "42"
assert after["loads"] == before["loads"] and after["registry_entries"] == 1
result = {"status": "PASS", "repairs": flow.repairs, "profile": profile, "mode": mode, "precision": base["precision"],
          "kv": base["kv_quantization"], "text": answer, "vision": color, "tool": call["function"],
          "tool_result": tool_reply["content"], "after_sdxl": after_answer, "sdxl_prompt": prompt,
          "memory": [{k: row[k] for k in ("loaded", "resident_bytes", "loads", "transfers", "registry_entries", "diagnostics")}
                     for row in (before, during, after)], "seconds": time.monotonic()-started}
(outdir / ("workflow-" + mode + ".json")).write_text(json.dumps(result, indent=2))
print(json.dumps(result), flush=True)
