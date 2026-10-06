import asyncio
import contextlib
import uuid
from PIL import Image
from . import assets
from .graph import graph
from .records import get, update


async def execute(e, sid, job):
    p = dict(job["args"])
    ident = job["id"]
    prompt_id = str(uuid.uuid4())
    p["output_key"] = sid + "-" + str(ident)
    source = mask = original = mask_image = None
    parents = []
    if "source" in p:
        original = await assets.load(e.db, e.comfy, sid, p["source"])
        original = original.resize((p["width"], p["height"]), Image.Resampling.LANCZOS)
        source = await e.comfy.upload(assets.png(original), prompt_id + ".png")
        parents.append(assets.resolve(e.db, sid, p["source"])["id"])
    if "mask" in p:
        mask_image = (await assets.load(e.db, e.comfy, sid, p["mask"])).convert("L")
        if mask_image.size != original.size:
            raise ValueError("Mask dimensions must match the source")
        mask = await e.comfy.upload(assets.png(mask_image), prompt_id + "-mask.png")
    async def event(message):
        data = message.get("data", {})
        if data.get("prompt_id") == prompt_id and message["type"] in ("progress", "executing", "execution_start"):
            update(e.db, sid, ident, progress={"type": message["type"], **data})
    watch = asyncio.create_task(e.comfy.events(prompt_id, event))
    update(e.db, sid, ident, prompt_id=prompt_id)
    try:
        await e.comfy.request("/prompt", {"prompt": graph(p, source, mask), "prompt_id": prompt_id, "client_id": prompt_id})
        result = await e.comfy.history(prompt_id, lambda: get(e.db, sid, ident).get("cancel"))
        if result["status"]["status_str"] != "success":
            raise ValueError(str(result["status"]["messages"])[-1600:])
        remote = result["outputs"]["7"]["images"][0]
        from urllib.parse import urlencode
        image = assets.decode(await e.comfy.request("/view?" + urlencode(remote), binary=True))
        if mask_image:
            image = Image.composite(image, original, mask_image)
        return assets.save(e.db, sid, image, job["mode"], parents,
            remote=None if mask_image else remote, settings=p, llm=job["settings"],
            comfy_output=remote, prompt_id=prompt_id, mask=p.get("mask"))
    finally:
        watch.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await watch
