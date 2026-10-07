import asyncio
import json
import logging
import uuid
from .gateway_graph import graph
from .gateway_link import get, disconnect
from .settings import read


async def execute(body, request=None, on_event=None):
    link = get()
    prompt_id = body.get("comfy_prompt_id") or str(uuid.uuid4())
    future = None
    gone = asyncio.create_task(disconnect(request))
    completed = False
    try:
        future = await link.events.subscribe(prompt_id, on_event)
        await link.request("/prompt", {"prompt": graph(body), "prompt_id": prompt_id,
                                       "client_id": link.events.client_id})
        timeout = read("config.yaml")["request_timeout"]
        done, _ = await asyncio.wait((future, gone), timeout=timeout, return_when=asyncio.FIRST_COMPLETED)
        if gone in done:
            await gone
        if future not in done:
            raise TimeoutError(f"LLM request exceeded {timeout}s; its ComfyUI prompt is being cancelled")
        await future
        history = await link.request("/history/" + prompt_id)
        result = history.get(prompt_id)
        if not result:
            raise RuntimeError("ComfyUI finished without recording the LLM result")
        if result["status"]["status_str"] != "success":
            raise RuntimeError("ComfyUI LLM execution failed; see its execution trace")
        value = json.loads(result["outputs"]["2"]["text"][0])
        completed = True
        return value
    finally:
        gone.cancel()
        await asyncio.gather(gone, return_exceptions=True)
        try:
            if not completed:
                await asyncio.shield(link.request(f"/api/jobs/{prompt_id}/cancel", {}))
            await asyncio.shield(link.request("/history", {"delete": [prompt_id]}))
        except Exception:
            logging.exception("ComfyUI prompt cleanup failed: %s", prompt_id)
        link.events.pending.pop(prompt_id, None)
        if future and not future.done():
            future.cancel()
        elif future and not future.cancelled():
            future.exception()
