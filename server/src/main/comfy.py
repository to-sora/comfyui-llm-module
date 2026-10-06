import asyncio
import json
import socket
import aiohttp
from .settings import read


class Comfy:
    async def start(self):
        cfg = read()
        self.url = cfg["gateway_url"].rstrip("/")
        if not self.url.startswith("https://"):
            raise ValueError("gateway_url requires HTTPS")
        self.timeout = cfg["request_timeout"]
        self.client = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(family=socket.AF_INET, ssl=False),
            timeout=aiohttp.ClientTimeout(total=self.timeout))

    async def request(self, path, body=None, method=None, binary=False, **kw):
        async with self.client.request(method or ("POST" if body is not None else "GET"),
                self.url + path, json=body, **kw) as response:
            if response.status >= 400:
                raise ValueError(f"ComfyUI {response.status}: {(await response.text())[:1200]}")
            return await response.read() if binary else await response.json()

    async def upload(self, data, name):
        form = aiohttp.FormData()
        form.add_field("image", data, filename=name, content_type="image/png")
        form.add_field("type", "input")
        form.add_field("overwrite", "true")
        reply = await self.request("/upload/image", method="POST", data=form)
        return "/".join(p for p in (reply.get("subfolder"), reply["name"]) if p)

    async def cancel(self, prompt_id):
        return await self.request(f"/api/jobs/{prompt_id}/cancel", {})

    async def events(self, client_id, callback):
        try:
            async with self.client.ws_connect(self.url + "/ws", params={"clientId": client_id}) as ws:
                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        await callback(json.loads(msg.data))
        except (aiohttp.ClientError, asyncio.TimeoutError):
            pass

    async def history(self, prompt_id, cancelled):
        deadline = asyncio.get_running_loop().time() + self.timeout
        while asyncio.get_running_loop().time() < deadline:
            if cancelled():
                await self.cancel(prompt_id)
            value = await self.request("/history/" + prompt_id)
            if prompt_id in value:
                return value[prompt_id]
            if cancelled():
                q = await self.request("/queue")
                if not any(row[1] == prompt_id for rows in q.values() for row in rows):
                    raise ValueError("Cancelled")
            await asyncio.sleep(0.25)
        raise TimeoutError("ComfyUI job timed out; inspect its prompt ID before retrying")
