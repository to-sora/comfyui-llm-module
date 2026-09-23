import os
import runpy
import sys
from pathlib import Path
from ipv4 import enable
from settings import APP, DATA, configure_paths, read_config
from network import addresses
from tls import certificate

configure_paths()
enable()
config = read_config("port-config.yaml")
key, cert = certificate()
comfy = APP / ".local-tool-app/ComfyUI"
os.chdir(comfy)
sys.path.insert(0, str(comfy))
sys.argv = [str(comfy / "main.py"), "--listen", ",".join(addresses(config)),
    "--port", str(config["port"]), "--tls-keyfile", str(key),
    "--tls-certfile", str(cert), "--base-directory", str(DATA / "comfy"),
    "--input-directory", str(DATA / "input"),
    "--output-directory", str(DATA / "output"),
    "--user-directory", str(DATA / "user"),
    "--temp-directory", str(DATA / "tmp"), "--disable-auto-launch"]
if os.environ.get("QWEN_CPU") == "1":
    sys.argv.append("--cpu")
runpy.run_path(str(comfy / "main.py"), run_name="__main__")
