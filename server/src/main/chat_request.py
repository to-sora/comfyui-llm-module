import asyncio
import uuid
from .records import get, update
from .prompt_cleanup import cleanup


async def complete(e, sid, ident, payload):
    prompt_id = str(uuid.uuid4())
    update(e.db, sid, ident, prompt_id=prompt_id)
    task = asyncio.create_task(e.comfy.request("/v1/chat/completions", {**payload, "comfy_prompt_id": prompt_id}))
    completed = False
    try:
        value = await task
        completed = True
        from .provenance import snapshot
        status = await e.comfy.request("/llm/status")
        update(e.db, sid, ident, actual_model={**snapshot(status, payload["model"]),
               "context_tokens": payload["context_tokens"]})
        if get(e.db, sid, ident).get("cancel"):
            raise RuntimeError("Generation was stopped")
        return value
    finally:
        if not task.done():
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)
        await cleanup(e.comfy, prompt_id, completed)
