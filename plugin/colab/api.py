import json
import ssl
import time
import urllib.error
import urllib.request

BASE = "https://127.0.0.1:8188"
CONTEXT = ssl._create_unverified_context()
OPENER = urllib.request.build_opener(
    urllib.request.ProxyHandler({}), urllib.request.HTTPSHandler(context=CONTEXT))


def request(path, body=None):
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(BASE + path, data=data,
                                 headers={"Content-Type": "application/json"})
    with OPENER.open(req, timeout=30) as response:
        return json.load(response)


def ready(seconds=900):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        try:
            info = request("/object_info")
            assert "QwenGenerate" in info, "Qwen extension import failed; plugin/data/comfy.log"
            return
        except (urllib.error.URLError, TimeoutError):
            time.sleep(2)
    raise TimeoutError("ComfyUI startup; plugin/data/comfy.log")


def execute(graph):
    posted = request("/prompt", {"prompt": graph})
    if posted.get("node_errors"):
        raise AssertionError(posted["node_errors"])
    ident = posted["prompt_id"]
    deadline = time.monotonic() + 600
    while time.monotonic() < deadline:
        history = request("/history/" + ident).get(ident)
        if history:
            assert history["status"]["status_str"] == "success", history["status"]
            return history["outputs"]["2"]["text"]
        time.sleep(1)
    raise TimeoutError(f"ComfyUI prompt {ident}")


def free_models():
    request("/free", {"unload_models": True, "free_memory": True})
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        state = request("/qwen/status")
        if all(not m["loaded"] for m in state["models"]):
            return state
        time.sleep(1)
    raise TimeoutError("ComfyUI model unload")
