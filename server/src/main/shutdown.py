import asyncio
from .records import flat


async def cancel_active(e):
    for session in e.db.sessions():
        for record in flat(e.db, session["id"]):
            if record["kind"] in ("job", "chat") and record.get("status") in ("queued", "running") and record.get("prompt_id"):
                try:
                    await asyncio.wait_for(e.comfy.cancel(record["prompt_id"]), 2)
                except Exception:
                    pass
