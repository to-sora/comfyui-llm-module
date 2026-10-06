from .ipv4 import enable
from .settings import environment


def initialize():
    enable()
    environment()
    from aiohttp import web
    from server import PromptServer
    from .gateway import install
    from .memory_policy import install as install_memory_policy
    from .network import install_whitelist
    from .runtime import status
    install_whitelist(PromptServer.instance.app)
    install_memory_policy()
    install()

    @PromptServer.instance.routes.get("/llm/status")
    async def report(request):
        return web.json_response(status())
