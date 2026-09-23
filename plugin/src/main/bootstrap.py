def initialize():
    from .ipv4 import enable
    from .settings import configure_paths, defaults
    configure_paths()
    enable()
    from server import PromptServer
    from aiohttp import web
    from .registry import snapshot, acquire, STARTUP
    from .spec import normalize

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
