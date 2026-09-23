def initialize():
    from .ipv4 import enable
    from .settings import configure_paths, defaults, read_config
    configure_paths()
    enable()
    from server import PromptServer
    from aiohttp import web
    from .registry import snapshot, acquire, STARTUP
    from .spec import normalize
    config = read_config("port-config.yaml")
    if config["enable_whitelist"]:
        from .network import whitelist
        allowed = whitelist(config)

        @web.middleware
        async def restrict(request, handler):
            if request.remote not in allowed:
                raise web.HTTPForbidden()
            return await handler(request)

        PromptServer.instance.app.middlewares.append(restrict)

    @PromptServer.instance.routes.get("/qwen/status")
    async def status(request):
        return web.json_response(snapshot())

    async def startup(app):
        import asyncio
        from comfy import model_management as mm
        for entry in defaults()["startup_models"]:
            engine = acquire(normalize(**entry))
            await asyncio.to_thread(mm.load_models_gpu, [engine.patcher],
                                    force_full_load=True)
            STARTUP.append(engine)

    PromptServer.instance.app.on_startup.append(startup)
