import asyncio
import uuid
from .comfy_socket import listen


class Events:
    def __init__(self, comfy):
        self.comfy = comfy
        self.client_id = uuid.uuid4().hex
        self.ready = asyncio.Event()
        self.pending = {}
        self.failure = "ComfyUI event connection has not opened"
        self.active = None
        self.task = asyncio.create_task(listen(self))

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
        if kind == "execution_start":
            self.active = data.get("prompt_id")
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

    async def close(self):
        self.task.cancel()
        await asyncio.gather(self.task, return_exceptions=True)
