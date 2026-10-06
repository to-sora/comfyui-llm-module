import asyncio
import time
from .comfy import Comfy
from .store import Store
from .discovery import discover
from .records import create, flat, get, update
from .settings import read


class Engine:
    def __init__(self):
        self.db = Store()
        self.comfy = Comfy()
        self.lock = asyncio.Lock()
        self.tasks = set()
        self.active = None
        self.caps = None
        self.connection_error = None

    async def start(self):
        await self.comfy.start()
        try:
            self.caps = await discover(self.comfy)
        except Exception as exc:
            self.connection_error = str(exc)
        if not self.db.active():
            self.db.new_session("Studio 1", self.caps["defaults"] if self.caps else {})
        from .recovery import recover
        await recover(self)

    def spawn(self, coroutine):
        task = asyncio.create_task(coroutine)
        self.tasks.add(task)
        task.add_done_callback(self.tasks.discard)
        return task

    def check_active(self, sid):
        if sid != self.db.active():
            raise ValueError("Select this session before using it")

    def pending(self, sid):
        return [r for r in flat(self.db, sid, "job") if r["status"] == "pending"]

    def enqueue(self, sid, mode, args, settings):
        if len(self.pending(sid)) >= read()["max_pending_jobs"]:
            raise ValueError("Pending list is full; submit or cancel jobs")
        return create(self.db, sid, "job", {"mode": mode, "args": args,
            "settings": settings, "status": "pending", "created": time.time()})

    def batch(self, sid):
        jobs = self.pending(sid)
        batch = create(self.db, sid, "batch", {"jobs": [j["id"] for j in jobs], "status": "queued"})
        for job in jobs:
            update(self.db, sid, job["id"], status="queued", batch=batch["id"])
        return batch

    async def cancel(self, sid, ident):
        value = get(self.db, sid, ident)
        if value["kind"] == "batch":
            for job in value["jobs"]:
                await self.cancel(sid, job)
        elif value["kind"] in ("job", "chat") and value["status"] in ("pending", "queued", "running"):
            update(self.db, sid, ident, cancel=True)
            if value.get("prompt_id"):
                await self.comfy.cancel(value["prompt_id"])
            elif value["status"] != "running":
                update(self.db, sid, ident, status="cancelled")
        return create(self.db, sid, "result", {"target": ident, "status": "cancel_requested"})

    async def close(self):
        for task in self.tasks:
            task.cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)
        await self.comfy.client.close()
        self.db.db.close()
