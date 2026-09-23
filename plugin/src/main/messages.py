def messages(prefix, prompt, images=None):
    result = [{"role": "system", "content": prefix}] if prefix else []
    content = prompt
    if images:
        content = [{"type": "image", "image": image} for image in images]
        content.append({"type": "text", "text": prompt})
    return result + [{"role": "user", "content": content}]


def pil_images(tensor):
    if tensor is None:
        return None
    from PIL import Image
    array = (tensor.detach().cpu().clamp(0, 1).numpy() * 255).round()
    return [Image.fromarray(item.astype("uint8")).convert("RGB")
            for item in array]


def llama_messages(prefix, prompt, images=None):
    import base64
    import io
    result = messages(prefix, prompt)
    if images:
        content = []
        for image in images:
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            uri = "data:image/png;base64," + base64.b64encode(
                buffer.getvalue()).decode("ascii")
            content.append({"type": "image_url", "image_url": {"url": uri}})
        content.append({"type": "text", "text": prompt})
        result[-1]["content"] = content
    return result
