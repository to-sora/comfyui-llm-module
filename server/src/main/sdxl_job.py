import asyncio
import contextlib
import uuid
from PIL import Image
from . import assets
from .graph import graph
from .records import get, update
from .sdxl_inputs import prepare


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
    ready = asyncio.Event()
    watch = asyncio.create_task(e.comfy.events(prompt_id, event, ready))
    update(e.db, sid, ident, prompt_id=prompt_id)
    try:
        await asyncio.wait_for(ready.wait(), 10)
        await e.comfy.request("/prompt", {"prompt": graph(p, source, mask), "prompt_id": prompt_id, "client_id": prompt_id})
        async def observe(q):
            queued = [row[1] for row in q["queue_pending"]]
            update(e.db, sid, ident, comfy_phase="queued" if prompt_id in queued else "running",
                   queue_position=queued.index(prompt_id) + 1 if prompt_id in queued else 0)
        result = await e.comfy.history(prompt_id, lambda: get(e.db, sid, ident).get("cancel"), observe)
        if result["status"]["status_str"] != "success":
            raise ValueError(str(result["status"]["messages"])[-1600:])
        remote = result["outputs"]["7"]["images"][0]
        from urllib.parse import urlencode
        image = assets.decode(await e.comfy.request("/view?" + urlencode(remote), binary=True))
        if mask_image:
            image = Image.composite(image.crop((0, 0, *original.size)), original, mask_image)
        return assets.save(e.db, sid, image, job["mode"], parents,
            remote=None if mask_image else remote, settings=p, requested_llm=job["settings"], actor=job.get("actor"),
            comfy_output=remote, prompt_id=prompt_id, mask=p.get("mask"))
    finally:
        watch.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await watch
