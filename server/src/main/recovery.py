from .records import flat, update


async def recover(e):
    for session in e.db.sessions():
        sid = session["id"]
        for item in flat(e.db, sid):
            if item["kind"] not in ("batch", "chat", "job") or item.get("status") not in ("queued", "running"):
                continue
            if item.get("prompt_id"):
                try:
                    await e.comfy.cancel(item["prompt_id"])
                except Exception:
                    pass
            update(e.db, sid, item["id"], status="interrupted",
                   error="Workbench restarted. Results remain in ComfyUI history; reuse settings to retry.")
