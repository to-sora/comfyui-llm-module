from .images import load_image
from .messages import normalize


def prepare(processor, vision, request, images):
    messages, tools = normalize(request)
    for message in messages:
        content = message.get("content")
        if content is None:
            message["content"] = ""
        elif isinstance(content, list):
            for item in content:
                if item["type"] == "image_url":
                    item["image"] = load_image(item.pop("image_url")["url"])
                    item["type"] = "image"
    if images:
        for message in reversed(messages):
            if message["role"] == "user":
                if isinstance(message["content"], str):
                    message["content"] = [{"type": "text", "text": message["content"]}]
                message["content"] += [{"type": "image", "image": image} for image in images]
                break
    if not processor.chat_template:
        raise ValueError("This checkpoint has no chat template. Configure its intended template before chat use.")
    return processor.apply_chat_template(
        messages, tools=tools, tokenize=True, add_generation_prompt=True,
        return_dict=True, return_tensors="pt",
        enable_thinking=request.get("enable_thinking", False))
