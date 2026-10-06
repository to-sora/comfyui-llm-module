import base64
import io
from . import assets


async def attach(e, sid, ids, text):
    content = [{"type": "text", "text": text}]
    for ident in ids[:4]:
        image = await assets.load(e.db, e.comfy, sid, ident)
        image.thumbnail((512, 512))
        stream = io.BytesIO()
        image.convert("RGB").save(stream, format="JPEG", quality=90)
        url = "data:image/jpeg;base64," + base64.b64encode(stream.getvalue()).decode()
        content.extend([{"type": "text", "text": f"Image #{ident}"},
                        {"type": "image_url", "image_url": {"url": url}}])
    return {"role": "user", "content": content}


def compact(message):
    result = dict(message)
    if isinstance(result.get("content"), list):
        result["content"] = [item if item["type"] == "text" else
            {"type": "text", "text": "[Image attached for this inference]"} for item in result["content"]]
    return result
