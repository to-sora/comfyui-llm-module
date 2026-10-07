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
    from .gateway_link import close
    PromptServer.instance.app.on_cleanup.append(close)
    from .network import install_whitelist
    from .runtime import status
    install_whitelist(PromptServer.instance.app)
    install()

    @PromptServer.instance.routes.get("/llm/status")
    async def report(request):
        return web.json_response(status())
