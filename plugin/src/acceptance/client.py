import json
import ssl
import time
import urllib.request
from pathlib import Path
import sys

MAIN = Path(__file__).resolve().parents[1] / "main"
sys.path.insert(0, str(MAIN))
from settings import DATA, ROOT, read_config
from ipv4 import enable

enable()
PORT = read_config("port-config.yaml")["port"]
URL = f"https://127.0.0.1:{PORT}"
CTX = ssl.create_default_context(cafile=str(DATA / "tls/cert.pem"))
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}),
    urllib.request.HTTPSHandler(context=CTX))


def call(path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    request = urllib.request.Request(URL + path, data=data,
                                     headers={"Content-Type": "application/json"})
    with OPENER.open(request, timeout=30) as response:
        return json.load(response)


def workflow(graph):
    result = call("/prompt", {"prompt": graph})
    key = result["prompt_id"]
    for _ in range(600):
        history = call("/history/" + key)
        if key in history:
            item = history[key]
            if item["status"]["status_str"] == "error":
                raise RuntimeError(str(item["status"]["messages"])[-1500:])
            return item["outputs"]["2"]["text"]
        time.sleep(1)
    raise TimeoutError("ComfyUI workflow exceeded 600 seconds")


def unload():
    call("/free", {"unload_models": True, "free_memory": True})
    for _ in range(60):
        state = call("/qwen/status")
        if all(not m["resident"] for m in state["models"]):
            return state
        time.sleep(1)
    raise TimeoutError("Native ComfyUI unload exceeded 60 seconds")
