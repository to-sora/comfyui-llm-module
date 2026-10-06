from .images import data_url, tensor_images, load_image
from .messages import normalize


def prepare(request, images):
    messages, tools = normalize(request)
    for message in messages:
        content = message.get("content")
        for part in content if isinstance(content, list) else []:
            if part.get("type") == "image_url":
                url = part["image_url"]["url"]
                if url.startswith(("https://", "http://")):
                    part["image_url"]["url"] = data_url(load_image(url))
    pictures = tensor_images(images)
    if pictures:
        user = next(m for m in reversed(messages) if m["role"] == "user")
        if isinstance(user["content"], str):
            user["content"] = [{"type": "text", "text": user["content"]}]
        user["content"] += [{"type": "image_url", "image_url": {"url": data_url(p)}} for p in pictures]
    return messages, tools
