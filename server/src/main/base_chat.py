from .settings import APP
from .tool_schema import tool, field


def is_base(e, model):
    return any(p["id"] == model and p.get("base_completion") for p in e.caps["profiles"])


def prepare(e, payload, sid, ident):
    if not is_base(e, payload["model"]):
        return payload
    from .records import flat
    jobs = [j for j in flat(e.db, sid, "job") if j["id"] > ident]
    payload["messages"][0]["content"] = (APP / "config/content-config/base-assistant.txt").read_text()
    if jobs and all(j["status"] == "done" for j in jobs):
        payload["tools"] = []
        payload["tool_choice"] = "none"
        images = next(m for m in reversed(payload["messages"]) if m["role"] == "user" and
            isinstance(m.get("content"), list) and any(p["type"] == "image_url" for p in m["content"]))
        images = {"role": "user", "content": [dict(p) for p in images["content"]]}
        images["content"][0]["text"] = "Describe the object colors and backgrounds in each of these generated images."
        payload["messages"] = [images]
        return payload
    if any(j["status"] == "pending" for j in jobs):
        payload["tools"] = [t for t in payload["tools"] if t["function"]["name"] == "sent_all_pending"]
        payload["tool_choice"] = "required"
        payload["messages"][0]["content"] = "All requested prompts have been queued. Call sent_all_pending now."
        return payload
    allowed = ("image_gen_sdxl_image", "view_images", "image_edit_basic")
    payload["tools"] = [t for t in payload["tools"] if t["function"]["name"] in allowed]
    for item in payload["tools"]:
        func = item["function"]
        if func["name"].startswith("image_gen_sdxl_"):
            props = func["parameters"]["properties"]
            func["parameters"]["properties"] = {k: v for k, v in props.items() if k in ("source", "prompt")}
    payload["tools"].append(tool("finish_response", "Answer the user without another operation.",
        {"text": field("string")}, ["text"]))
    from .queue_batch import schema
    payload["tools"].insert(0, schema())
    payload["tool_choice"] = "required"
    return payload
