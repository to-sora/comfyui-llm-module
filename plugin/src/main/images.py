import base64
import io
import requests
from PIL import Image
from urllib.parse import urlsplit
from .settings import APP, read
from .errors import UserError

LIMIT = 16 * 1024**2


def validate_url(url):
    if not isinstance(url, str):
        raise UserError("Image URL must be text")
    if url.startswith("data:image/"):
        if len(url) > LIMIT * 4 // 3 + 256:
            raise UserError("Image input exceeds 16 MB")
        return
    parsed = urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname not in ("127.0.0.1", "localhost") or parsed.port != read("port-config.yaml")["port"]:
        raise UserError("Use an image data URL or this ComfyUI server's HTTPS image URL")


def load_image(url):
    validate_url(url)
    if url.startswith("data:image/"):
        content = base64.b64decode(url.split(",", 1)[1], validate=True)
    else:
        with requests.get(url, timeout=30, verify=str(APP / "data/tls/cert.pem"),
                          stream=True, allow_redirects=False) as response:
            if response.status_code != 200:
                raise UserError(f"Image request returned HTTP {response.status_code}")
            chunks, count = [], 0
            for chunk in response.iter_content(65536):
                count += len(chunk)
                if count > LIMIT:
                    raise UserError("Image input exceeds 16 MB")
                chunks.append(chunk)
            content = b"".join(chunks)
    if len(content) > LIMIT:
        raise UserError("Image input exceeds 16 MB")
    return Image.open(io.BytesIO(content)).convert("RGB")


def tensor_images(tensor):
    if tensor is None:
        return []
    return [Image.fromarray((x.detach().cpu().numpy().clip(0, 1) * 255).astype("uint8")) for x in tensor]


def data_url(picture):
    buffer = io.BytesIO()
    picture.save(buffer, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode()
