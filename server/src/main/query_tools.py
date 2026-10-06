from . import assets
from .records import create, get


async def invoke(e, sid, name, args):
    if name == "check_current_pending":
        return create(e.db, sid, "result", {"jobs": e.pending(sid)})
    if name == "job_status":
        job = get(e.db, sid, args["id"])
        return create(e.db, sid, "result", {"target": args["id"], "job": job})
    if name == "cancel_job":
        return await e.cancel(sid, args["id"])
    if name == "list_models":
        return create(e.db, sid, "result", {"models": e.caps["profiles"], "checkpoints": e.caps["checkpoints"]})
    if name == "image_settings":
        from .model_tools import select
        return select(e, sid, args)
    if name == "view_images":
        ids = [assets.resolve(e.db, sid, x)["id"] for x in args["ids"]]
        if not 1 <= len(ids) <= 4:
            raise ValueError("View 1–4 images per call")
        return create(e.db, sid, "result", {"images": ids, "status": "attached"})
    raise ValueError("Unknown tool")
