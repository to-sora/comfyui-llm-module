import ipaddress
import socket
from .settings import read


def port_config():
    cfg = read("port-config.yaml")
    if cfg["policy"] not in {"local", "standard", "public"}:
        raise ValueError("policy: local | standard | public")
    if not 1 <= cfg["port"] <= 65535:
        raise ValueError("port: 1..65535")
    cfg["allowed"] = {str(ipaddress.IPv4Address(ip.strip()))
                      for ip in cfg["whitelist"].split(",") if ip.strip()}
    return cfg


def hosts(cfg):
    if cfg["policy"] == "local":
        return "127.0.0.1"
    if cfg["policy"] == "public":
        return "0.0.0.0"
    import psutil
    addresses = sorted({a.address for name, entries in psutil.net_if_addrs().items()
                        if name.startswith(("wg", "tails"))
                        for a in entries if a.family == socket.AF_INET})
    if not addresses:
        raise RuntimeError("standard policy requires wg*/tails* IPv4 interface")
    return ",".join(addresses)


def install_whitelist(app):
    from aiohttp import web
    cfg = port_config()
    if not cfg["enable_whitelist"]:
        return

    @web.middleware
    async def guard(request, handler):
        if request.remote not in cfg["allowed"]:
            raise web.HTTPForbidden()
        return await handler(request)

    app.middlewares.append(guard)
