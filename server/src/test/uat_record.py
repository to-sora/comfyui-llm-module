import json
import time
import traceback
from datetime import datetime, timezone
from browser_session import browser
from uat_common import OUT, save, snapshot, state
from browser_helpers import until
from client import call
from uat_plain import run

started = time.monotonic()
proof = {"started_utc": datetime.now(timezone.utc).isoformat(), "browser": "Firefox",
         "scope": "Current engine branch; redesign and five-profile acceptance are pending"}
def ready():
    try:
        return bool(call("/bootstrap").get("capabilities"))
    except OSError:
        return False
until(ready, timeout=60)
with browser() as driver:
    try:
        sid = run(driver, proof)
        proof["status"] = "PASS"
    except Exception as exc:
        proof.update(status="FAIL", error=str(exc) or type(exc).__name__)
        snapshot(driver, "failure")
        if proof.get("session"):
            save("failure-state", state(proof["session"]))
        (OUT / "failure.txt").write_text(traceback.format_exc()[-2900:])
    finally:
        proof["elapsed_seconds"] = round(time.monotonic() - started, 1)
        save("result", proof)
        print(json.dumps({k: proof[k] for k in ("status", "session", "error", "elapsed_seconds") if k in proof}), flush=True)
        print("Evidence:", OUT, flush=True)
if proof["status"] != "PASS":
    raise SystemExit(1)
