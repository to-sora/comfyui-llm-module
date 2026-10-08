import asyncio
import socket
import aiohttp
from .settings import read
from .comfy_events import Events


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
        self.events = Events(self)
        self.cancelled = set()

    async def request(self, path, body=None, method=None, binary=False, **kw):
        async with self.client.request(method or ("POST" if body is not None else "GET"),
                self.url + path, json=body, **kw) as response:
            if response.status >= 400:
                raise RuntimeError(f"ComfyUI {response.status}: {(await response.text())[:1200]}")
            return await response.read() if binary else await response.json()

    async def upload(self, data, name):
        form = aiohttp.FormData()
        form.add_field("image", data, filename=name, content_type="image/png")
        form.add_field("type", "input")
        form.add_field("overwrite", "true")
        reply = await self.request("/upload/image", method="POST", data=form)
        return "/".join(p for p in (reply.get("subfolder"), reply["name"]) if p)

    async def cancel(self, prompt_id):
        if prompt_id in self.cancelled:
            return
        self.cancelled.add(prompt_id)
        try:
            async with self.client.post(self.url + f"/api/jobs/{prompt_id}/cancel", json={},
                                        timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status in (404, 409):
                    self.cancelled.discard(prompt_id)
                if response.status not in (200, 404, 409):
                    raise RuntimeError(f"Cannot cancel ComfyUI prompt: HTTP {response.status}")
        except BaseException:
            self.cancelled.discard(prompt_id)
            raise

    async def history(self, prompt_id, future):
        try:
            await asyncio.wait_for(asyncio.shield(future), self.timeout)
        except TimeoutError as exc:
            raise TimeoutError(f"ComfyUI prompt {prompt_id} exceeded {self.timeout}s") from exc
        value = await self.request("/history/" + prompt_id)
        if prompt_id not in value:
            raise RuntimeError("ComfyUI finished without recording the result")
        return value[prompt_id]

    async def close(self):
        await self.events.close()
        await self.client.close()
