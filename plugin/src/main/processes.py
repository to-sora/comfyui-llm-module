import json
import os
import signal
import psutil
from .settings import APP

STATE = APP / "data" / "service.json"


def listeners(port):
    result = {}
    for item in psutil.net_connections(kind="tcp4"):
        if item.status == psutil.CONN_LISTEN and item.laddr.port == port:
            pid = item.pid
            name = psutil.Process(pid).name() if pid else "unknown"
            result[pid] = name
    return result


def terminate(pid, group=False):
    try:
        process = psutil.Process(pid)
        children = process.children(recursive=True)
        if group:
            os.killpg(pid, signal.SIGTERM)
        else:
            for child in children:
                child.terminate()
            process.terminate()
        _, alive = psutil.wait_procs([process, *children], timeout=4)
        for item in alive:
            item.kill()
    except (ProcessLookupError, psutil.NoSuchProcess):
        pass


def stop():
    if not STATE.exists():
        return
    saved = json.loads(STATE.read_text())
    try:
        process = psutil.Process(saved["pid"])
        if process.create_time() == saved["created"]:
            terminate(process.pid, group=True)
    except psutil.NoSuchProcess:
        pass
    STATE.unlink(missing_ok=True)


def record(pid):
    STATE.write_text(json.dumps({"pid": pid, "created": psutil.Process(pid).create_time()}))
