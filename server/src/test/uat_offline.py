import hashlib
import io
import socket
import urllib.error
import urllib.request
from PIL import Image
from browser_session import browser
from browser_helpers import until
from client import call, BASE, CTX
from uat_common import save, snapshot, state

with socket.socket(socket.AF_INET) as sock:
    assert sock.connect_ex(("127.0.0.1", 8188)) != 0, "This test requires ComfyUI to be stopped"
sid = call("/bootstrap")["active"]
item = next(i for i in state(sid)["images"] if not i.get("readonly") and i["operation"] == "sdxl_text")
url = BASE + f'/session/{sid}/image/{item["id"]}'
with urllib.request.urlopen(url, context=CTX) as response:
    raw = response.read()
    etag, cache = response.headers["ETag"], response.headers["Cache-Control"]
assert hashlib.sha256(raw).hexdigest() == item["sha256"]
assert "immutable" in cache
try:
    urllib.request.urlopen(urllib.request.Request(url, headers={"If-None-Match": etag}), context=CTX)
    raise AssertionError("Cached image did not return 304")
except urllib.error.HTTPError as exc:
    assert exc.code == 304, exc
with urllib.request.urlopen(url + "?thumb=1", context=CTX) as response:
    image = Image.open(io.BytesIO(response.read()))
    assert image.format == "WEBP"
with browser() as driver:
    driver.set_window_rect(width=1440, height=1100)
    driver.navigate("https://127.0.0.1:8189")
    until(lambda: driver.execute_script("return document.getElementById('main-image')?.naturalWidth>0"), timeout=30)
    assert driver.execute_script("return document.getElementById('connection').textContent") == "Gateway unavailable"
    snapshot(driver, "offline-library")
save("offline-images", {"status": "PASS", "comfyui_stopped": True, "image": item["id"],
     "bytes_match_recorded_sha256": True, "etag": etag, "conditional_status": 304,
     "cache_control": cache, "thumbnail": "WEBP", "browser_image_visible": True})
print("Offline image bytes, conditional caching, WebP and Firefox display PASS", flush=True)
