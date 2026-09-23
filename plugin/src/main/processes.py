import json
import os
import signal
import psutil
from settings import DATA

STATE = DATA / "process.json"


def occupants(port):
    return sorted({c.pid for c in psutil.net_connections(kind="tcp4")
                   if c.pid and c.status == "LISTEN" and c.laddr.port == port})


def terminate(pids):
    targets = {}
    for pid in pids:
        try:
            parent = psutil.Process(pid)
            for process in parent.children(recursive=True) + [parent]:
                targets[process.pid] = process
        except psutil.NoSuchProcess:
            pass
    for process in targets.values():
        try:
            process.terminate()
        except psutil.NoSuchProcess:
            pass
    _, alive = psutil.wait_procs(list(targets.values()), timeout=5)
    for process in alive:
        try:
            process.kill()
        except psutil.NoSuchProcess:
            pass
    psutil.wait_procs(alive, timeout=5)


def stop():
    if not STATE.exists():
        return
    state = json.loads(STATE.read_text())
    targets = []
    for process in psutil.process_iter(["pid", "create_time"]):
        try:
            if (os.getpgid(process.pid) == state["pid"]
                    and process.create_time() >= state["created"]):
                targets.append(process.pid)
        except (ProcessLookupError, psutil.NoSuchProcess):
            pass
    terminate(targets)
    STATE.unlink(missing_ok=True)


def remember(process):
    STATE.write_text(json.dumps({"pid": process.pid,
        "created": psutil.Process(process.pid).create_time()}))
