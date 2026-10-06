import argparse
import fcntl
import json
import signal
import subprocess
import sys
from .network import port_config
from .processes import STATE, listeners, record, stop, terminate
from .settings import DATA, prepare
from .tls import certificate


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--stop", action="store_true")
    group.add_argument("--force", action="store_true")
    args = parser.parse_args()
    prepare()
    with (DATA / "service.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if args.stop:
            stop()
            return 0
        cfg = port_config()
        if args.force:
            stop()
        occupied = listeners(cfg["port"])
        if occupied:
            print(f"Port / 連接埠 {cfg['port']}: {occupied}", flush=True)
            if not args.force:
                return 1
            for pid in occupied:
                if pid is None:
                    raise RuntimeError("Cannot identify port owner")
                terminate(pid)
        certificate()
        child = subprocess.Popen([sys.executable, "-m", "server.src.main.app"],
                                 start_new_session=True)
        record(child.pid)
    try:
        code = child.wait()
        return 0 if code == -signal.SIGTERM else code
    except KeyboardInterrupt:
        terminate(child.pid, group=True)
        return 130
    finally:
        if STATE.exists() and json.loads(STATE.read_text())["pid"] == child.pid:
            STATE.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
