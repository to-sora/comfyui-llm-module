import time
from . import cpu_job, sdxl_job
from .records import get, update


async def run(e, sid, ident):
    batch = get(e.db, sid, ident, "batch")
    if batch["status"] not in ("queued", "running"):
        return batch
    update(e.db, sid, ident, status="running")
    memory = [{"phase": "before", "state": await e.comfy.request("/llm/status")}]
    images = []
    for jid in batch["jobs"]:
        job = get(e.db, sid, jid, "job")
        if job["status"] == "done":
            images.append(job["image"])
            continue
        if job.get("cancel") or job["status"] == "cancelled":
            update(e.db, sid, jid, status="cancelled")
            continue
        update(e.db, sid, jid, status="running", started=time.time())
        try:
            worker = cpu_job if job["mode"] == "cpu" else sdxl_job
            asset = await worker.execute(e, sid, job)
            images.append(asset["id"])
            update(e.db, sid, jid, status="done", image=asset["id"], finished=time.time())
        except Exception as exc:
            cancelled = get(e.db, sid, jid).get("cancel")
            update(e.db, sid, jid, status="cancelled" if cancelled else "failed", error=str(exc))
        memory.append({"phase": "job", "job": jid, "state": await e.comfy.request("/llm/status")})
    statuses = [get(e.db, sid, j)["status"] for j in batch["jobs"]]
    status = "failed" if "failed" in statuses else "cancelled" if "cancelled" in statuses else "done"
    return update(e.db, sid, ident, status=status, images=images, memory=memory)


async def scheduled(e, sid, ident):
    async with e.lock:
        e.active = {"session": sid, "kind": "batch", "id": ident}
        try:
            await run(e, sid, ident)
        except Exception as exc:
            update(e.db, sid, ident, status="failed", error=str(exc))
        finally:
            e.active = None
