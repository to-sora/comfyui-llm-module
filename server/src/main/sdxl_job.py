import asyncio
import uuid
from PIL import Image
from . import assets
from .graph import graph
from .records import get, update
from .sdxl_inputs import prepare
from .prompt_cleanup import cleanup


async def execute(e, sid, job):
    p = dict(job["args"])
    ident = job["id"]
    prompt_id = str(uuid.uuid4())
    p["output_key"] = sid + "-" + str(ident)
    source, mask, original, mask_image, parents = await prepare(e, sid, p, prompt_id)
    async def event(message):
        data = message.get("data", {})
        if data.get("prompt_id") == prompt_id and message["type"] in ("progress", "executing", "execution_start"):
            old = get(e.db, sid, ident).get("progress", {})
            update(e.db, sid, ident, progress={**old, "type": message["type"], **data}, comfy_phase="running")
    future = None
    completed = False
    update(e.db, sid, ident, prompt_id=prompt_id)
    try:
        future = await e.comfy.events.subscribe(prompt_id, event)
        await e.comfy.request("/prompt", {"prompt": graph(p, source, mask), "prompt_id": prompt_id,
                                          "client_id": e.comfy.events.client_id})
        result = await e.comfy.history(prompt_id, future)
        if result["status"]["status_str"] != "success":
            raise RuntimeError(str(result["status"]["messages"])[-1600:] or "SDXL execution failed")
        completed = True
        remote = result["outputs"]["7"]["images"][0]
        from urllib.parse import urlencode
        raw = await e.comfy.request("/view?" + urlencode(remote), binary=True)
        image = assets.decode(raw)
        if mask_image:
            image = Image.composite(image.crop((0, 0, *original.size)), original, mask_image)
        return assets.save(e.db, sid, image, "sdxl_" + job["mode"], parents,
            content=None if mask_image else raw, settings=p, requested_llm=job["settings"], actor=job.get("actor"),
            comfy_output=remote, prompt_id=prompt_id, mask=p.get("mask"))
    finally:
        await cleanup(e.comfy, prompt_id, completed, future)
