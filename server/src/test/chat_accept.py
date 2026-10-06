import sys
from client import call, session, wait, save

model = sys.argv[1] if len(sys.argv) > 1 else "Qwen3.5-9B"
sid = session("Assistant · " + model)
profiles = {p["id"]: p for p in call("/bootstrap")["capabilities"]["profiles"]}
kv = "q8_0" if profiles[model]["backend"] == "gguf" else "hqq_8"
call(f"/session/{sid}/settings", {"model": model, "kv_quantization": kv,
     "width": 512, "height": 512, "steps": 12, "max_tokens": 700})
chat = call(f"/session/{sid}/chat", {"text": "Generate two images: a red toy car on a white background, and a blue mug on a white background. Queue both first, call sent_all_pending once, then inspect the actual final images and state the visible colors."})
print("Started", model, sid, chat["id"], flush=True)
result, state = wait(sid, "chats", chat["id"])
summary = {"model": model, "session": sid, "status": result["status"],
    "response": result.get("response"), "error": result.get("error"),
    "tools": [m.get("name") for m in state["messages"] if m["role"] == "tool"],
    "images": [i["id"] for i in state["images"] if not i.get("readonly")], "kv": kv}
save("chat-" + model, summary)
measurements = []
for batch in state["batches"]:
    for entry in batch.get("memory", []):
        mem = entry["state"]
        measurements.append({"phase": entry["phase"], "job": entry.get("job"),
            "free": mem["cuda_free"], "models": [{k: m[k] for k in ("model", "loaded", "resident_bytes", "loads")}
                                               for m in mem["models"] if m["model"] == model]})
if result.get("memory"):
    mem = result["memory"]
    measurements.append({"phase": "return_to_llm", "free": mem["cuda_free"],
        "models": [{k: m[k] for k in ("model", "loaded", "resident_bytes", "loads")} for m in mem["models"] if m["model"] == model]})
save("memory-" + model, measurements)
print(summary, flush=True)
assert result["status"] == "done", summary
assert result.get("response") and all(c in result["response"].lower() for c in ("red", "blue")), summary
assert len(summary["images"]) == 2, summary
assert "sent_all_pending" in summary["tools"], summary
