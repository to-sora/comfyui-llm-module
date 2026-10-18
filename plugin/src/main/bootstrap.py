from .ipv4 import enable
from .settings import environment


def initialize():
    enable()
    environment()
    from .diagnostics import install as install_diagnostics
    install_diagnostics()
    from aiohttp import web
    from server import PromptServer
    from .gateway import install
    from .route_access import Routes
    from .runtime import status
    install()

    @Routes(PromptServer.instance.routes).get("/llm/status")
    async def report(request):
        return web.json_response(status())
