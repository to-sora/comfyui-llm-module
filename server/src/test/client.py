import io
import json
import ssl
import time
import urllib.request
import uuid
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "fan-out/workbench"
OUT.mkdir(parents=True, exist_ok=True)
BASE = "https://127.0.0.1:8189/api"
CTX = ssl._create_unverified_context()


def call(path, body=None, binary=False):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, context=CTX, timeout=120) as response:
        raw = response.read()
    return raw if binary else json.loads(raw)


def session(name):
    return call("/sessions", {"name": name})["id"]


def tool(sid, name, args=None, request_id=None):
    return call(f"/session/{sid}/tool", {"name": name, "arguments": args or {},
                                        "request_id": request_id or str(uuid.uuid4())})


def wait(sid, kind, ident, seconds=1200):
    start = time.monotonic()
    while time.monotonic() - start < seconds:
        state = call(f"/session/{sid}/state")
        item = next(x for x in state[kind] if x["id"] == ident)
        if item["status"] not in ("queued", "running", "pending"):
            return item, state
        time.sleep(0.4)
    raise TimeoutError(f"{kind} {ident} did not finish")


def upload(sid, image, mask=False):
    stream = io.BytesIO()
    image.save(stream, format="PNG")
    boundary = uuid.uuid4().hex
    body = (f'--{boundary}\r\nContent-Disposition: form-data; name="image"; filename="input.png"\r\n'
            'Content-Type: image/png\r\n\r\n').encode() + stream.getvalue() + f'\r\n--{boundary}--\r\n'.encode()
    req = urllib.request.Request(BASE + f"/session/{sid}/upload" + ("?mask=1" if mask else ""), data=body,
        headers={"Content-Type": "multipart/form-data; boundary=" + boundary})
    with urllib.request.urlopen(req, context=CTX) as r:
        return json.load(r)


def picture(sid, ident):
    return Image.open(io.BytesIO(call(f"/session/{sid}/image/{ident}", binary=True))).convert("RGBA")


def save(name, data):
    (OUT / (name + ".json")).write_text(json.dumps(data, ensure_ascii=False, indent=2))
