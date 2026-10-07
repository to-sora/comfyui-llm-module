import logging
from .errors import message
from .chat import run
from .records import get, update


async def scheduled(e, sid, ident):
    async with e.lock:
        if get(e.db, sid, ident).get("cancel"):
            return
        e.active = {"session": sid, "kind": "chat", "id": ident}
        update(e.db, sid, ident, status="running")
        try:
            await run(e, sid, ident)
        except Exception as exc:
            logging.exception("Worker failed")
            update(e.db, sid, ident, status="cancelled" if get(e.db, sid, ident).get("cancel")
                   else "failed", error=message(exc))
        finally:
            e.active = None
