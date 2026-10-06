import base64
import io
from PIL import Image

TOOL = {"type": "function", "function": {
    "name": "get_weather", "description": "Get current weather for a city.",
    "parameters": {"type": "object", "properties": {"city": {"type": "string"}},
                   "required": ["city"]}}}


def user(text):
    return {"role": "user", "content": text}


def image_message(color):
    picture = Image.new("RGB", (256, 256), color)
    buffer = io.BytesIO()
    picture.save(buffer, format="PNG")
    url = "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode()
    return {"role": "user", "content": [
        {"type": "text", "text": "What color is this image? Reply with one word."},
        {"type": "image_url", "image_url": {"url": url}}]}
