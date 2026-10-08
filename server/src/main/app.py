import logging
import logging.handlers
import ssl
from aiohttp import web
from .studio import routes as studio_routes
from .studio.engine import Engine
from .network import hosts, port_config, install_whitelist
from .settings import APP, DATA, prepare, read
from .tls import certificate
from .errors import UserError, message


@web.middleware
async def errors(request, handler):
    try:
        response = await handler(request)
        response.headers.setdefault("Cache-Control", "no-cache")
        return response
    except UserError as exc:
        return web.json_response({"error": message(exc)}, status=400)
    except web.HTTPException:
        raise
    except Exception as exc:
        logging.exception("Request failed")
        return web.json_response({"error": message(exc)}, status=500)


async def build():
    app = web.Application(middlewares=[errors], client_max_size=read()["upload_mb"] * 1024**2)
    engine = Engine()
    await engine.start()
    app["engine"] = engine
    routes = web.RouteTableDef()
    studio_routes.install(routes, engine)
    app.add_routes(routes)
    async def page(request):
        return web.FileResponse(APP / "web-studio/index.html")
    for path in ('/', '/chats/{id}', '/library'):
        app.router.add_get(path, page)
    app.router.add_static("/static", APP / "web-studio")
    install_whitelist(app)
    async def close(app):
        await engine.close()
    app.on_cleanup.append(close)
    return app


def main():
    prepare()
    handler = logging.handlers.RotatingFileHandler(DATA / "service.log", maxBytes=10*1024**2, backupCount=4)
    logging.basicConfig(level=logging.INFO, handlers=[handler, logging.StreamHandler()])
    cert, key = certificate()
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(cert, key)
    config = port_config()
    web.run_app(build(), host=hosts(config).split(","), port=config["port"], ssl_context=context, access_log=None)


if __name__ == "__main__":
    main()
