import time
from concurrent.futures import ThreadPoolExecutor
from client import call, session, tool, wait, save

sid = session("Acceptance · Queue")
call(f"/session/{sid}/settings", {"width": 512, "height": 512, "steps": 300})
args = {"prompt": "A green apple on a white table", "seed": 88}
with ThreadPoolExecutor(max_workers=2) as pool:
    futures = [pool.submit(tool, sid, "image_gen_sdxl_text", args, "same-click") for _ in range(2)]
    repeats = [f.result() for f in futures]
assert repeats[0]["id"] == repeats[1]["id"]
pending = tool(sid, "image_gen_sdxl_text", args)
tool(sid, "cancel_job", {"id": pending["id"]})
batch = tool(sid, "sent_all_pending")
progress = None
for _ in range(250):
    state = call(f"/session/{sid}/state")
    job = next(j for j in state["jobs"] if j["id"] == repeats[0]["id"])
    progress = job.get("progress", {})
    if progress.get("value", 0) >= 2:
        break
    time.sleep(.2)
assert progress.get("max") == 300, job
tool(sid, "cancel_job", {"id": job["id"]})
result, state = wait(sid, "batches", batch["id"])
assert result["status"] == "cancelled", result
bad = tool(sid, "image_gen_sdxl_text", {"prompt": "test", "checkpoint": "missing.safetensors"})
assert "error" in bad
save("jobs", {"session": sid, "duplicate_id": repeats[0]["id"],
    "real_sampling_progress": {k: progress[k] for k in ("value", "max")},
    "selected_cancel": result["status"], "invalid_model_rejected": True, "status": "PASS"})
print("Concurrent retry deduplication, progress, cancellation and invalid model PASS")
