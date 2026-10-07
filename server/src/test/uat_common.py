import base64
import gzip
import json
import os
import time
from pathlib import Path
from client import ROOT, call
from browser_helpers import until

OUT = ROOT / "fan-out/uat-2026-10-08" / os.environ.get("UAT_RUN", "baseline")
OUT.mkdir(parents=True, exist_ok=True)


def save(name, value):
    raw = json.dumps(value, ensure_ascii=False, indent=2).encode()
    if len(raw) > 3000:
        (OUT / (name + ".json.gz")).write_bytes(gzip.compress(raw))
    else:
        (OUT / (name + ".json")).write_bytes(raw)


def snapshot(driver, name, width=None, height=None):
    if width:
        driver.set_window_rect(width=width, height=height)
    time.sleep(.4)
    (OUT / (name + ".png")).write_bytes(base64.b64decode(driver.screenshot()))
    return driver.execute_script("return {width:innerWidth,height:innerHeight,"
        "overflow:document.documentElement.scrollWidth>innerWidth}")


def state(sid):
    return call(f"/session/{sid}/state")


def finished(sid, kind, previous=-1):
    value = state(sid)
    rows = [r for r in value[kind] if r["id"] > previous]
    return value if rows and not value["busy"] else None


def wait_work(driver, sid, kind, previous=-1):
    last = 0
    def check():
        nonlocal last
        value = finished(sid, kind, previous)
        if time.monotonic() - last > 30:
            value_now = value or state(sid)
            print(kind, [(j["id"], j["status"]) for j in value_now[kind][-3:]], flush=True)
            snapshot(driver, "progress")
            last = time.monotonic()
        return value
    value = until(check, timeout=900)
    save(kind + "-state", value)
    item = value[kind][-1]
    assert item["status"] == "done", item.get("error", item)
    return value


def show(driver, ident):
    driver.execute_script("document.getElementById(arguments[0]).scrollIntoView({block:'center'})",
                          script_args=[ident])


def save_image(sid, ident, name):
    (OUT / (name + ".png")).write_bytes(call(f"/session/{sid}/image/{ident}", binary=True))
