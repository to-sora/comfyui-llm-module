from .errors import UserError
import json
from aiohttp import web
from .records import flat
from .sharing import available
from .settings import DATA
from .fonts import catalog
from .edit_schema import definitions
from .tool_schema import schemas
from .discovery import discover, llm_settings


def install(routes, e):
    @routes.get("/api/bootstrap")
    async def bootstrap(request):
        return web.json_response({"sessions": e.db.sessions(), "active": e.db.active(),
            "capabilities": e.caps, "error": e.connection_error, "gateway": e.comfy.url,
            "fonts": sorted(catalog()), "edits": definitions()})

    @routes.post("/api/reconnect")
    async def reconnect(request):
        e.caps = await discover(e.comfy)
        e.connection_error = None
        return web.json_response(e.caps)

    @routes.post("/api/sessions")
    async def sessions(request):
        if e.tasks:
            raise UserError("Wait for work to finish or cancel it before switching sessions")
        data = await request.json()
        if data.get("id"):
            e.db.activate(data["id"])
        else:
            e.db.new_session(data.get("name", "Untitled"), e.caps["defaults"] if e.caps else {})
        return web.json_response({"id": e.db.active()})

    @routes.get("/api/session/{sid}/state")
    async def state(request):
        sid = request.match_info["sid"]
        e.check_active(sid)
        own = [v for v in flat(e.db, sid, "image") if not v.get("deleted")]
        shared = available(e.db, sid)
        granted = {r[0] for r in e.db.sql("SELECT target FROM shares WHERE owner=? AND enabled=1", (sid,))}
        for image in own:
            image["shared"] = image["id"] in granted
        size = sum(p.stat().st_size for p in DATA.rglob("*") if p.is_file())
        return web.json_response({"session": e.db.session(sid), "images": own + shared,
            "lineage": [{k: i[k] for k in ("id", "operation", "parents", "deleted", "final") if k in i}
                        for i in flat(e.db, sid, "image")], "events": flat(e.db, sid, "event"),
            "jobs": flat(e.db, sid, "job"), "batches": flat(e.db, sid, "batch"),
            "chats": flat(e.db, sid, "chat"), "messages": flat(e.db, sid, "message")[-100:],
            "active": e.active, "busy": bool(e.tasks), "storage_bytes": size,
            "referenced_bytes": sum(i.get("bytes", 0) for i in own if i.get("remote"))})

    @routes.post("/api/session/{sid}/settings")
    async def settings(request):
        sid = request.match_info["sid"]
        e.check_active(sid)
        value = {**e.db.session(sid)["settings"], **await request.json()}
        llm_settings(e.caps, value)
        e.db.sql("UPDATE sessions SET settings=? WHERE id=?", (json.dumps(value), sid))
        return web.json_response(value)

    @routes.get("/api/tools")
    async def tools(request):
        return web.json_response(schemas(e.caps, expanded=True))
