import json
from aiohttp import web
from server import PromptServer
from .gateway_jobs import execute
from .protocol import validate
from .registry import profiles
from .settings import read


async def stream_response(request, result):
    response = web.StreamResponse(headers={"Content-Type": "text/event-stream",
                                           "Cache-Control": "no-cache"})
    await response.prepare(request)
    choice = result["choices"][0]
    delta = dict(choice["message"])
    for i, call in enumerate(delta.get("tool_calls", [])):
        call["index"] = i
    chunk = {k: result[k] for k in ("id", "created", "model")}
    chunk.update(object="chat.completion.chunk",
                 choices=[{"index": 0, "delta": delta, "finish_reason": None}])
    await response.write(("data: " + json.dumps(chunk) + "\n\n").encode())
    chunk["choices"] = [{"index": 0, "delta": {}, "finish_reason": choice["finish_reason"]}]
    await response.write(("data: " + json.dumps(chunk) + "\n\ndata: [DONE]\n\n").encode())
    await response.write_eof()
    return response


def install():
    routes = PromptServer.instance.routes

    @routes.get("/v1/models")
    async def models(request):
        return web.json_response({"object": "list", "data": [
            {"id": name, "object": "model", "owned_by": "local"} for name in profiles()]})

    @routes.post("/v1/chat/completions")
    async def chat(request):
        try:
            body = validate(await request.json())
            if PromptServer.instance.prompt_queue.get_tasks_remaining() >= read("config.yaml")["queue_limit"]:
                return web.json_response({"error": {"message": "ComfyUI queue is full."}}, status=429)
            result = await execute(body)
            return await stream_response(request, result) if body.get("stream") else web.json_response(result)
        except (ValueError, KeyError, TypeError) as exc:
            return web.json_response({"error": {"message": str(exc), "type": "invalid_request_error"}}, status=400)
        except (RuntimeError, TimeoutError) as exc:
            return web.json_response({"error": {"message": str(exc), "type": "execution_error"}}, status=500)
