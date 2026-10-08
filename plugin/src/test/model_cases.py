import base64
import io
from PIL import Image

MEMORY_SYSTEM = 'You are a concise assistant for image planning and questions. Answer accurately, remember the user preferences, and respect the requested output format. Explain limitations clearly and never invent facts. Use the conversation to understand references to earlier messages. Keep your final answer brief and useful.'
MEMORY_SYSTEM += ' When discussing images, rely on visible evidence. Keep track of earlier edits and distinguish requests from completed results. If information is missing, state the limit instead of making up an answer.'

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
