import logging
from .ipv4 import enable
from .settings import environment, options, read

PRELOADED = []


def initialize():
    enable()
    environment()
    from aiohttp import web
    from server import PromptServer
    from .runtime import get_handle, status
    from .network import install_whitelist
    install_whitelist(PromptServer.instance.app)

    @PromptServer.instance.routes.get("/qwen/status")
    async def report(request):
        import asyncio
        return web.json_response(await asyncio.to_thread(status))

    for item in read("config.yaml")["startup_models"]:
        try:
            handle = get_handle(options(**item))
            with handle.pool.lease(handle.ensure):
                pass
            PRELOADED.append(handle)
        except Exception:
            logging.exception("Qwen startup prefill failed / Qwen 啟動預填失敗")
