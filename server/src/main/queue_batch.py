from .errors import UserError
from .records import create
from .settings import read


def schema():
    from .tool_schema import tool, field
    return tool("image_gen_sdxl_batch", "Queue all requested images together, ONE prompt per separate image. Uses UI defaults. Then call sent_all_pending.",
        {"prompts": field("array", items=field("string"), minItems=1, maxItems=32)}, ["prompts"])


async def queue(e, sid, args, inline):
    from .tools import invoke
    prompts = args.get("prompts")
    if not isinstance(prompts, list) or not prompts or any(not isinstance(p, str) or not p.strip() for p in prompts):
        raise UserError("prompts must be a nonempty array of image descriptions")
    if len(prompts) + len(e.pending(sid)) > read()["max_pending_jobs"]:
        raise UserError("Too many pending images")
    jobs = [await invoke(e, sid, "image_gen_sdxl_text", {"prompt": p}, inline) for p in prompts]
    return create(e.db, sid, "result", {"status": "pending", "jobs": [j["id"] for j in jobs]})
