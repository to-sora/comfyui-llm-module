from .errors import UserError
import asyncio
import logging
from .errors import message
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
            logging.exception("Gateway connection failed")
            self.connection_error = message(exc)
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
            raise UserError("Select this session before using it")

    def pending(self, sid):
        return [r for r in flat(self.db, sid, "job") if r["status"] == "pending"]

    def enqueue(self, sid, mode, args, settings, actor):
        if len(self.pending(sid)) >= read()["max_pending_jobs"]:
            raise UserError("Pending list is full; submit or cancel jobs")
        return create(self.db, sid, "job", {"mode": mode, "args": args,
            "settings": settings, "actor": actor, "status": "pending", "created": time.time()})

    def batch(self, sid):
        jobs = self.pending(sid)
        batch = create(self.db, sid, "batch", {"jobs": [j["id"] for j in jobs], "status": "queued"})
        for job in jobs:
            update(self.db, sid, job["id"], status="queued", batch=batch["id"])
        return batch

    async def cancel(self, sid, ident):
        from .job_cancel import cancel
        return await cancel(self, sid, ident)

    async def close(self):
        from .shutdown import cancel_active
        await cancel_active(self)
        for task in self.tasks:
            task.cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)
        await self.comfy.close()
        self.db.db.close()
