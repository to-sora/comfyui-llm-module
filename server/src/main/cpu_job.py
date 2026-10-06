import asyncio
from . import assets, edit_color, edit_geometry, edit_text


async def execute(e, sid, job):
    args = job["args"]
    source = assets.resolve(e.db, sid, args["source"])
    image = await assets.load(e.db, e.comfy, sid, source["id"])
    op, params = args["operation"], args["params"]
    parents = [source["id"]]
    overlay = None
    if op == "overlay":
        overlay = await assets.load(e.db, e.comfy, sid, int(params["overlay"]))
        parents.append(assets.resolve(e.db, sid, int(params["overlay"]))["id"])
    if op == "text":
        output = await asyncio.to_thread(edit_text.apply, image, params)
    elif op in ("crop", "resize", "rotate", "flip", "pad", "overlay"):
        output = await asyncio.to_thread(edit_geometry.apply, image, op, params, overlay)
    else:
        output = await asyncio.to_thread(edit_color.apply, image, op, params)
    return assets.save(e.db, sid, output, op, parents, parameters=params,
                       requested_llm=job["settings"], actor=job.get("actor"),
                       source_settings=source.get("settings", source.get("source_settings")))
