import time
from datetime import datetime, timezone
from browser_session import browser
from browser_helpers import until
from client import call
from uat_common import save, snapshot, state
from uat_edits import text_edit
from uat_masks import run as masks
from uat_layouts import run as layouts

sid = call("/bootstrap")["active"]
started = time.monotonic()
result = {"session": sid, "started_utc": datetime.now(timezone.utc).isoformat(), "cases": []}
with browser() as driver:
    driver.set_window_rect(width=1440, height=1100)
    driver.navigate("https://127.0.0.1:8189")
    until(lambda: driver.execute_script("return document.getElementById('main-image')?.naturalWidth>0"))
    for name, test in (("text-lineage-refresh-brush", text_edit), ("upload-inpaint", masks), ("layout-download", layouts)):
        try:
            value = test(driver, sid)
            row = {"case": name, "status": "PASS", **value}
        except Exception as exc:
            row = {"case": name, "status": "FAIL", "error": str(exc) or type(exc).__name__}
            snapshot(driver, name + "-failure")
        result["cases"].append(row)
        save(name, row)
        print(row, flush=True)
    save("edits-state", state(sid))
result["elapsed_seconds"] = round(time.monotonic() - started, 1)
save("edits-result", result)
print(result, flush=True)
if any(r["status"] == "FAIL" for r in result["cases"]):
    raise SystemExit(1)
