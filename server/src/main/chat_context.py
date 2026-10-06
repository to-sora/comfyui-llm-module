import json
from .records import flat
from .tool_schema import schemas


def brief(result):
    if result.get("kind") == "job":
        return {k: result[k] for k in ("id", "status", "mode")}
    if "jobs" in result and isinstance(result["jobs"], list):
        result = dict(result)
        result["jobs"] = [{k: j[k] for k in ("id", "mode", "status") if k in j}
                          if isinstance(j, dict) else j for j in result["jobs"]]
    return result


def build(e, sid, ident, messages):
    jobs = [j for j in flat(e.db, sid, "job") if j["id"] > ident]
    inventory = [{k: j[k] for k in ("id", "status", "mode", "image") if k in j}
                 | {"prompt": j["args"].get("prompt", j["args"].get("operation", ""))[:160]}
                 for j in jobs]
    note = "Existing work for this request; do not repeat it: " + json.dumps(inventory)
    base = [dict(messages[0]), messages[1]]
    base[0]["content"] += "\n" + note
    start = next((i for i in range(len(messages)-1, 1, -1) if messages[i]["role"] == "assistant"), len(messages))
    base.extend(messages[start:])
    last_images = next((m for m in reversed(messages[2:]) if m["role"] == "user" and
        isinstance(m.get("content"), list) and any(p["type"] == "image_url" for p in m["content"])), None)
    if last_images and last_images not in base:
        base.append(last_images)
    selected = schemas(e.caps)
    last_tool = next((m for m in reversed(messages) if m["role"] == "tool"), {})
    if '"checkpoints"' in last_tool.get("content", ""):
        from .model_tools import schema
        selected = [schema(e.caps)]
    if jobs and all(j["status"] == "done" for j in jobs):
        selected = [t for t in selected if t["function"]["name"] in (
            "view_images", "image_edit_basic", "image_gen_sdxl_image", "sent_all_pending")]
        base[0]["content"] += "\nThe requested batch is complete. Inspect the attached final pixels and answer the user."
    return base, selected
