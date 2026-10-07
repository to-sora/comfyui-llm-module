import asyncio
import json
import logging
import uuid
import aiohttp


class Events:
    def __init__(self, comfy):
        self.comfy = comfy
        self.client_id = uuid.uuid4().hex
        self.ready = asyncio.Event()
        self.pending = {}
        self.failure = "ComfyUI event connection has not opened"
        self.task = asyncio.create_task(self.listen())

    async def subscribe(self, ident, callback):
        try:
            await asyncio.wait_for(self.ready.wait(), 10)
        except TimeoutError as exc:
            raise RuntimeError(self.failure) from exc
        future = asyncio.get_running_loop().create_future()
        future.terminal = asyncio.Event()
        self.pending[ident] = (future, callback)
        return future

    async def dispatch(self, value):
        data, kind = value.get("data", {}), value.get("type")
        item = self.pending.get(data.get("prompt_id"))
        if not item:
            return
        future, callback = item
        if kind == "executing" and data.get("node") is None:
            future.terminal.set()
        if future.done():
            return
        if callback:
            try:
                await callback(value)
            except Exception as exc:
                future.set_exception(exc)
                return
        if kind in ("execution_error", "execution_interrupted"):
            future.set_exception(RuntimeError(data.get("exception_message") or "ComfyUI generation was interrupted"))
        elif kind == "executing" and data.get("node") is None:
            future.set_result(data)

    async def listen(self):
        delay = 0.5
        while True:
            try:
                async with self.comfy.client.ws_connect(self.comfy.url + "/ws",
                        params={"clientId": self.client_id}, heartbeat=20) as ws:
                    self.ready.set()
                    delay = 0.5
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            await self.dispatch(json.loads(msg.data))
                    raise ConnectionError("ComfyUI event connection closed")
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                logging.exception("ComfyUI event connection failed")
                self.failure = str(exc).strip() or "ComfyUI event connection failed"
                self.ready.clear()
                for future, _ in self.pending.values():
                    if not future.done():
                        future.set_exception(ConnectionError(self.failure))
                await asyncio.sleep(delay)
                delay = min(delay * 2, 30)

    async def close(self):
        self.task.cancel()
        await asyncio.gather(self.task, return_exceptions=True)
