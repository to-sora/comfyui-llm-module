import json
import os
import ssl
import time
import urllib.request

API = os.environ.get("COMFY_TEST_URL", "https://127.0.0.1:8188")
TLS = ssl._create_unverified_context()


def request(path, data=None, binary=False):
    payload = None if data is None else json.dumps(data).encode()
    req = urllib.request.Request(API + path, payload,
                                 {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, context=TLS, timeout=900) as response:
        content = response.read()
    return content if binary else json.loads(content)


def execute(graph, timeout=600):
    submitted = request("/prompt", {"prompt": graph})
    prompt_id = submitted["prompt_id"]
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        history = request("/history/" + prompt_id)
        if prompt_id in history:
            result = history[prompt_id]
            if result["status"]["status_str"] != "success":
                raise RuntimeError(json.dumps(result["status"], ensure_ascii=False))
            return prompt_id, result["outputs"]
        time.sleep(0.5)
    raise TimeoutError(f"ComfyUI prompt still unfinished: {prompt_id}")
