from .images import data_url, tensor_images
from .messages import normalize


def prepare(request, images):
    messages, tools = normalize(request)
    pictures = tensor_images(images)
    if pictures:
        user = next(m for m in reversed(messages) if m["role"] == "user")
        if isinstance(user["content"], str):
            user["content"] = [{"type": "text", "text": user["content"]}]
        user["content"] += [{"type": "image_url", "image_url": {"url": data_url(p)}} for p in pictures]
    return messages, tools
