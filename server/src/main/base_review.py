from .chat_images import attach
from .chat_request import complete
from .records import create, update


async def inspect(e, sid, ident, settings, images):
    observations = []
    for index, image_id in enumerate(images):
        update(e.db, sid, ident, review_index=index + 1, review_total=len(images))
        parts = []
        for label, question in (("Object", "What is the main object in this image?"),
                                ("Color", "What is the main object color?"),
                                ("Background", "Describe the background of this image.")):
            user = await attach(e, sid, [image_id], question)
            reply = await complete(e, sid, ident, {**settings, "max_tokens": min(settings["max_tokens"], 180),
                "messages": [user], "tools": [], "tool_choice": "none", "temperature": 0})
            text = reply["choices"][0]["message"].get("content")
            if not text:
                raise ValueError(f"No {label.lower()} observation for image #{image_id}")
            parts.append(label + ": " + text)
        observations.append(f"Image #{image_id}\n" + "\n".join(parts))
    text = "\n\n".join(observations)
    create(e.db, sid, "message", {"role": "assistant", "content": text, "chat": ident})
    return update(e.db, sid, ident, status="done", response=text,
                  memory=await e.comfy.request("/llm/status"))
