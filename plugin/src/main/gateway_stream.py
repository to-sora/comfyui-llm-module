import asyncio
import logging
from aiohttp import web
from .gateway_jobs import execute
from .sse_frames import Frames
from .errors import message


async def stream_response(request, body):
    response = web.StreamResponse(headers={"Content-Type": "text/event-stream",
                                           "Cache-Control": "no-cache"})
    await response.prepare(request)
    frames = Frames(response, body["model"])
    queue = asyncio.Queue(maxsize=512)
    async def event(value):
        if value.get("type") == "llm.token":
            queue.put_nowait(value["data"]["delta"])
    job = asyncio.create_task(execute(body, request, event))
    emitted = ""
    try:
        await frames.delta({"role": "assistant"})
        while not job.done() or not queue.empty():
            getter = asyncio.create_task(queue.get())
            try:
                ready, _ = await asyncio.wait((job, getter), timeout=15, return_when=asyncio.FIRST_COMPLETED)
                if getter in ready:
                    part = getter.result()
                    emitted += part
                    await frames.delta({"content": part})
                elif job in ready:
                    break
                else:
                    await response.write(b": keepalive\n\n")
            finally:
                getter.cancel()
                await asyncio.gather(getter, return_exceptions=True)
        result = await job
        choice = result["choices"][0]
        msg = choice["message"]
        content = msg.get("content") or ""
        if msg.get("tool_parse_error"):
            await frames.delta({k: msg[k] for k in ("tool_parse_error", "raw_output")})
        elif content.startswith(emitted):
            if content[len(emitted):]:
                await frames.delta({"content": content[len(emitted):]})
        else:
            raise RuntimeError("Generated content disagrees with the token stream")
        if msg.get("tool_calls"):
            await frames.delta({"tool_calls": [dict(call, index=i) for i, call in enumerate(msg["tool_calls"])]})
        await frames.delta({}, choice["finish_reason"])
        if body.get("stream_options", {}).get("include_usage"):
            await frames.value({**frames.meta, "choices": [], "usage": result["usage"]})
        await frames.done()
    except Exception as exc:
        logging.exception("LLM stream failed")
        if request.transport and not request.transport.is_closing():
            await frames.value({"error": {"message": message(exc), "type": "execution_error"}})
            await frames.done()
    finally:
        job.cancel()
        await asyncio.gather(job, return_exceptions=True)
    return response
