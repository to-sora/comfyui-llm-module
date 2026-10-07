from .errors import json_body
import json
import logging
from aiohttp import web
from server import PromptServer
from .gateway_jobs import execute
from .protocol import validate
from .registry import profiles
from .settings import read
from .errors import UserError, message
from .gateway_stream import stream_response


def install():
    routes = PromptServer.instance.routes
    from .capabilities import install as install_capabilities
    install_capabilities(routes)
    from .token_count import install as install_token_count
    install_token_count(routes)

    @routes.get("/v1/models")
    async def models(request):
        return web.json_response({"object": "list", "data": [
            {"id": name, "object": "model", "owned_by": "local"} for name in profiles()]})

    @routes.post("/v1/chat/completions")
    async def chat(request):
        try:
            body = validate(await json_body(request))
            if PromptServer.instance.prompt_queue.get_tasks_remaining() >= read("config.yaml")["queue_limit"]:
                return web.json_response({"error": {"message": "ComfyUI queue is full."}}, status=429)
            if body.get("stream"):
                return await stream_response(request, body)
            return web.json_response(await execute(body, request))
        except UserError as exc:
            return web.json_response({"error": {"message": message(exc), "type": "invalid_request_error"}}, status=400)
        except Exception as exc:
            logging.exception("LLM gateway request failed")
            return web.json_response({"error": {"message": message(exc), "type": "execution_error"}}, status=500)
