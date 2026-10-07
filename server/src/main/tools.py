from .errors import UserError, required
from . import assets, batches
from .records import create, get, update
from .discovery import llm_settings
from .image_options import options
from .edit_schema import validate
from .provenance import actor


async def invoke(e, sid, name, args, inline=False):
    if not isinstance(name, str) or not isinstance(args, dict):
        raise UserError("Tool name and arguments must be text and an object")
    e.check_active(sid)
    settings = e.db.session(sid)["settings"]
    if not e.caps:
        raise UserError(e.connection_error or "Connect to the gateway first")
    if name == "image_gen_sdxl_batch":
        from .queue_batch import queue
        return await queue(e, sid, args, inline)
    if name.startswith("image_gen_sdxl_"):
        mode = name.removeprefix("image_gen_sdxl_")
        if mode not in ("text", "image", "inpaint"):
            raise UserError("Unknown SDXL operation")
        values = options(e.caps, settings, args, mode)
        for field in (["source", "mask"] if mode == "inpaint" else ["source"] if mode == "image" else []):
            value = get(e.db, sid, required(args, field))
            if value["kind"] not in ("image", "job"):
                raise UserError("Source and mask must refer to images")
            values[field] = args[field]
        return e.enqueue(sid, mode, values, llm_settings(e.caps, settings), actor(e, sid, inline))
    if name.startswith("image_edit_"):
        operation = args.get("operation") if name == "image_edit_basic" else name.removeprefix("image_edit_")
        params = args.get("params", {k: v for k, v in args.items() if k not in ("source", "operation")})
        get(e.db, sid, required(args, "source"))
        return e.enqueue(sid, "cpu", {"source": args["source"], "operation": operation,
            "params": validate(operation, params)}, llm_settings(e.caps, settings), actor(e, sid, inline))
    if name in ("sent_all_pending", "pending_sent"):
        from .batch_guard import check
        check(e, sid, inline)
        if not e.pending(sid):
            return create(e.db, sid, "result", {"status": "empty", "jobs": [], "images": []})
        batch = e.batch(sid)
        if inline:
            if e.active and e.active["kind"] == "chat":
                update(e.db, sid, e.active["id"], batch=batch["id"])
            batch = await batches.run(e, sid, batch["id"])
        else:
            e.spawn(batches.scheduled(e, sid, batch["id"]))
        return {k: batch[k] for k in ("id", "status", "jobs", "images") if k in batch}
    from .query_tools import invoke as query
    return await query(e, sid, name, args)
