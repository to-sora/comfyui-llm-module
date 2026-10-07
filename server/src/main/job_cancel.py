from .records import create, get, update


async def cancel(e, sid, ident):
    value = get(e.db, sid, ident)
    if value["kind"] == "batch":
        for job in value["jobs"]:
            await cancel(e, sid, job)
    elif value["kind"] in ("job", "chat") and value["status"] in ("pending", "queued", "running"):
        update(e.db, sid, ident, cancel=True)
        if value.get("batch") is not None and value["kind"] == "chat":
            await cancel(e, sid, value["batch"])
        if value.get("prompt_id"):
            await e.comfy.cancel(value["prompt_id"])
        elif value["status"] != "running":
            update(e.db, sid, ident, status="cancelled")
    return create(e.db, sid, "result", {"target": ident, "status": "cancel_requested"})
