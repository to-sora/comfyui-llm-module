import argparse
import subprocess
import sys
import time
import ssl
import urllib.request
import psutil
from ipv4 import enable
from settings import APP, DATA, configure_paths, read_config
from network import addresses
from processes import occupants, remember, stop, terminate

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
group.add_argument("--force", action="store_true")
group.add_argument("--stop", action="store_true")
args = parser.parse_args()
configure_paths()
enable()
if args.stop:
    stop()
    raise SystemExit(0)
config = read_config("port-config.yaml")
pids = occupants(config["port"])
for pid in pids:
    print(f"Port {config['port']}: PID {pid} {psutil.Process(pid).name()}")
if pids and not args.force:
    raise SystemExit(1)
if args.force:
    terminate(pids)
stop()
with (DATA / "comfy.log").open("w") as log:
    child = subprocess.Popen([sys.executable, str(APP / "src/main/serve.py")],
        stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
remember(child)
host = addresses(config)[0]
url = f"https://{'127.0.0.1' if host == '0.0.0.0' else host}:{config['port']}"
context = ssl._create_unverified_context()
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}),
    urllib.request.HTTPSHandler(context=context))
try:
    for _ in range(300):
        if child.poll() is not None:
            raise RuntimeError((DATA / "comfy.log").read_text()[-4000:])
        try:
            with opener.open(url + "/system_stats", timeout=2) as response:
                if response.status == 200:
                    print(f"Ready / 啟動完成: {url}")
                    print(f"Trust self-signed certificate / 信任自簽憑證: {DATA / 'tls/cert.pem'}")
                    break
        except (OSError, urllib.error.URLError):
            time.sleep(1)
    else:
        raise TimeoutError("ComfyUI startup timeout; inspect plugin/data/comfy.log")
except BaseException:
    stop()
    raise
