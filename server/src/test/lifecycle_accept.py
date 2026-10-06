import json
import subprocess
import time
import urllib.request
from client import call, session, tool, save, ROOT, CTX

script = str(ROOT / "server/start.sh")


def ready():
    for _ in range(180):
        try:
            result = call("/bootstrap")
            if result["capabilities"]:
                return result
        except OSError:
            pass
        time.sleep(.3)
    raise TimeoutError("Workbench did not start")


def start(*args):
    state_file = ROOT / "server/data/service.json"
    old = json.loads(state_file.read_text())["pid"] if state_file.exists() else None
    proc = subprocess.Popen([script, *args], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(100):
        if state_file.exists() and json.loads(state_file.read_text())["pid"] != old:
            break
        time.sleep(.1)
    ready()
    return proc


subprocess.run([script, "--stop"], check=True)
first = start()
conflict = subprocess.run([script], capture_output=True, text=True)
assert conflict.returncode == 1 and "8189" in conflict.stdout and "python" in conflict.stdout, conflict.stdout
second = start("--force")
first.wait(timeout=8)
sid = session("Acceptance · Restart")
call(f"/session/{sid}/settings", {"steps": 500, "width": 512, "height": 512})
job = tool(sid, "image_gen_sdxl_text", {"prompt": "A yellow flower", "seed": 192})
tool(sid, "sent_all_pending")
for _ in range(150):
    state = call(f"/session/{sid}/state")
    current = next(j for j in state["jobs"] if j["id"] == job["id"])
    if current.get("progress", {}).get("value", 0) >= 2:
        break
    time.sleep(.2)
assert current.get("prompt_id")
subprocess.run([script, "--stop"], check=True)
second.wait(timeout=8)
third = start()
state = call(f"/session/{sid}/state")
item = next(j for j in state["jobs"] if j["id"] == job["id"])
assert item["status"] in ("interrupted", "failed", "cancelled"), item
with urllib.request.urlopen("https://127.0.0.1:8188/queue", context=CTX) as r:
    queue = json.load(r)
assert not any(row[1] == current["prompt_id"] for rows in queue.values() for row in rows)
save("lifecycle", {"session": sid, "port_conflict_reported": True, "force_replaced": True,
    "restart_job_status": item["status"], "owned_comfy_job_stopped": True, "status": "PASS"})
subprocess.run([script, "--stop"], check=True)
third.wait(timeout=8)
print("Start/stop, PID reporting, --force and interrupted-work recovery PASS")
