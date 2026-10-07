import asyncio
import json
import socket
import aiohttp
from .gateway_events import Events
from .network import hosts, port_config

LINK = None


class Link:
    def __init__(self):
        config = port_config()
        host = "127.0.0.1" if config["policy"] == "public" else hosts(config).split(",")[0]
        self.url = f"https://{host}:{config['port']}"
        self.client = aiohttp.ClientSession(connector=aiohttp.TCPConnector(
            family=socket.AF_INET, ssl=False), timeout=aiohttp.ClientTimeout(total=30))
        self.events = Events(self)

    async def request(self, path, body=None):
        async with self.client.request("POST" if body is not None else "GET", self.url+path, json=body) as response:
            raw = await response.text()
            if response.status >= 400:
                raise RuntimeError(f"ComfyUI {response.status}: {raw or response.reason}")
            return json.loads(raw) if raw.strip() else None

    async def close(self):
        await self.events.close()
        await self.client.close()

    async def cancel(self, prompt_id):
        async with self.client.post(self.url + f"/api/jobs/{prompt_id}/cancel", json={}) as response:
            if response.status not in (200, 404, 409):
                raise RuntimeError(f"ComfyUI cancellation failed: HTTP {response.status}")


def get():
    global LINK
    if LINK is None:
        LINK = Link()
    return LINK


async def close(app):
    global LINK
    if LINK is not None:
        await LINK.close()
        LINK = None


async def disconnect(request):
    while request is not None and request.transport is not None and not request.transport.is_closing():
        await asyncio.sleep(0.1)
    if request is None:
        await asyncio.Future()
    raise ConnectionError("The requesting client disconnected")
