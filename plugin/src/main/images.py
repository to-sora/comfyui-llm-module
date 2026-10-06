import base64
import io
import requests
from PIL import Image


def load_image(url):
    if url.startswith("data:image/"):
        content = base64.b64decode(url.split(",", 1)[1], validate=True)
    elif url.startswith(("https://", "http://")):
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        content = response.content
    else:
        raise ValueError("Image input must be an HTTP(S) URL or base64 image data URL.")
    return Image.open(io.BytesIO(content)).convert("RGB")


def tensor_images(tensor):
    if tensor is None:
        return []
    return [Image.fromarray((x.detach().cpu().numpy().clip(0, 1) * 255).astype("uint8"))
            for x in tensor]


def data_url(picture):
    buffer = io.BytesIO()
    picture.save(buffer, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode()
