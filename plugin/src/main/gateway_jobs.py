import asyncio
import json
import logging
import uuid
from .gateway_graph import graph
from .gateway_link import get, disconnect
from .settings import read
from .gateway_cleanup import cleanup


async def execute(body, request=None, on_event=None):
    link = get()
    prompt_id = body.get("comfy_prompt_id") or str(uuid.uuid4())
    body = {**body, "comfy_prompt_id": prompt_id, "comfy_client_id": link.events.client_id}
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
        await asyncio.shield(cleanup(link, prompt_id, completed, future))
