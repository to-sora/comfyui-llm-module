import asyncio
import uuid
from .records import get, update


async def complete(e, sid, ident, payload):
    prompt_id = str(uuid.uuid4())
    update(e.db, sid, ident, prompt_id=prompt_id)
    task = asyncio.create_task(e.comfy.request("/v1/chat/completions", {**payload, "comfy_prompt_id": prompt_id}))
    try:
        while not task.done():
            if get(e.db, sid, ident).get("cancel"):
                await e.comfy.cancel(prompt_id)
            await asyncio.wait([task], timeout=0.25)
        value = await task
        from .provenance import snapshot
        status = await e.comfy.request("/llm/status")
        update(e.db, sid, ident, actual_model={**snapshot(status, payload["model"]),
               "context_tokens": payload["context_tokens"]})
        if get(e.db, sid, ident).get("cancel"):
            raise ValueError("Cancelled")
        return value
    finally:
        if not task.done():
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)
