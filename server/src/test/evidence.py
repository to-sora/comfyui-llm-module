import json
import sqlite3
from client import ROOT, OUT, save

db = sqlite3.connect(ROOT / "server/data/workbench.sqlite")
rows = []
for path in sorted(OUT.glob("chat-*.json")):
    test = json.loads(path.read_text())
    if "model" not in test:
        continue
    model, sid = test["model"], test["session"]
    records = [(kind, json.loads(raw)) for kind, raw in db.execute(
        "SELECT kind,data FROM records WHERE session=? ORDER BY id", (sid,))]
    batch = next(d for kind, d in records if kind == "batch" and d["status"] == "done")
    chat = next(d for kind, d in records if kind == "chat" and d["status"] == "done")
    before = batch["memory"][0]["state"]
    during = batch["memory"][1]["state"]
    after = chat["memory"]
    resident = lambda s: sum(m["resident_bytes"] for m in s["models"] if m["model"] == model and m["loaded"])
    switch = [v for v in during["events"] if v.get("event") == "switch" and v.get("to") == "diffusion"][-1]
    released = switch["cuda_free_after"] - switch["cuda_free_before"]
    assert resident(before) > 0 and resident(during) == 0 and resident(after) > 0 and released > 0
    assert test["status"] == "done" and len(test["images"]) == 2
    assert all(c in test["response"].lower() for c in ("red", "blue"))
    proof = {"model": model, "session": sid, "llm_bytes": [resident(before), resident(during), resident(after)],
             "cuda_free_increase_bytes": released, "quantization": next(m["quantization"] for m in before["models"] if m["model"] == model),
             "kv": test["kv"], "images": test["images"], "tools": test["tools"], "status": "PASS"}
    save("proof-" + model, proof)
    rows.append(proof)
save("models", [{"model": r["model"], "released_gib": round(r["cuda_free_increase_bytes"] / 1024**3, 2),
                 "kv": r["kv"], "status": r["status"]} for r in rows])
assert len(rows) == 5
print("Five original models: real tool calls, actual image colors and CUDA unload/reload proven")
