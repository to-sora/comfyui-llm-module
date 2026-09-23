import argparse
import fcntl
import signal
import subprocess
import sys
from .network import hosts, port_config
from .processes import STATE, listeners, record, stop, terminate
from .settings import APP, environment, read
from .tls import certificate


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--stop", action="store_true")
    group.add_argument("--force", action="store_true")
    parser.add_argument("--cpu", action="store_true")
    args = parser.parse_args()
    environment()
    lock_path = APP / "data" / "service.lock"
    with lock_path.open("a") as lock:
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
                    raise RuntimeError("Port owner PID requires process visibility")
                terminate(pid)
        cert, key = certificate()
        comfy = (APP / read("config.yaml")["comfy_directory"]).resolve()
        cmd = [sys.executable, "-m", "plugin.src.main.comfy_entry", str(comfy),
               "--listen", hosts(cfg), "--port", str(cfg["port"]),
               "--tls-keyfile", str(key), "--tls-certfile", str(cert),
               "--disable-auto-launch", "--user-directory", str(APP / "data/user"),
               "--input-directory", str(APP / "data/input"),
               "--output-directory", str(APP / "data/output"),
               "--temp-directory", str(APP / "data/tmp")]
        if args.cpu:
            cmd.append("--cpu")
        child = subprocess.Popen(cmd, cwd=APP.parent, start_new_session=True)
        record(child.pid)
    try:
        code = child.wait()
        if code == -signal.SIGTERM:
            return 0
        return 128 - code if code < 0 else code
    except KeyboardInterrupt:
        terminate(child.pid, group=True)
        return 130
    finally:
        if STATE.exists():
            import json
            if json.loads(STATE.read_text())["pid"] == child.pid:
                STATE.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
