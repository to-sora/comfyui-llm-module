from . import assets, batches
from .records import create, get, update
from .discovery import llm_settings
from .image_options import options
from .edit_schema import validate
from .provenance import actor


async def invoke(e, sid, name, args, inline=False):
    e.check_active(sid)
    settings = e.db.session(sid)["settings"]
    if not e.caps:
        raise ValueError(e.connection_error or "Connect to the gateway first")
    if name.startswith("image_gen_sdxl_"):
        mode = name.removeprefix("image_gen_sdxl_")
        if mode not in ("text", "image", "inpaint"):
            raise ValueError("Unknown SDXL operation")
        values = options(e.caps, settings, args)
        for field in (["source", "mask"] if mode == "inpaint" else ["source"] if mode == "image" else []):
            value = get(e.db, sid, args[field])
            if value["kind"] not in ("image", "job"):
                raise ValueError("Source and mask must refer to images")
            values[field] = args[field]
        return e.enqueue(sid, mode, values, llm_settings(e.caps, settings), actor(e, sid, inline))
    if name.startswith("image_edit_"):
        operation = args.get("operation") if name == "image_edit_basic" else name.removeprefix("image_edit_")
        params = args.get("params", {k: v for k, v in args.items() if k not in ("source", "operation")})
        get(e.db, sid, args["source"])
        return e.enqueue(sid, "cpu", {"source": args["source"], "operation": operation,
            "params": validate(operation, params)}, llm_settings(e.caps, settings), actor(e, sid, inline))
    if name in ("sent_all_pending", "pending_sent"):
        batch = e.batch(sid)
        if inline:
            if e.active and e.active["kind"] == "chat":
                update(e.db, sid, e.active["id"], batch=batch["id"])
            batch = await batches.run(e, sid, batch["id"])
        else:
            e.spawn(batches.scheduled(e, sid, batch["id"]))
        return {k: batch[k] for k in ("id", "status", "jobs", "images") if k in batch}
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
