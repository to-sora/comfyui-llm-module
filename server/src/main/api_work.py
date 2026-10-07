from .errors import UserError
import asyncio
import json
from aiohttp import web
from . import tools, chat_worker, assets
from .records import create
from .errors import required


def install(routes, e):
    commands = asyncio.Lock()

    @routes.post("/api/session/{sid}/tool")
    async def tool(request):
        sid = request.match_info["sid"]
        e.check_active(sid)
        body = await request.json()
        async with commands:
            key = sid + ":" + str(body.get("request_id", ""))
            saved = e.db.sql("SELECT value FROM meta WHERE key=?", (key,)).fetchone() if body.get("request_id") else None
            if saved:
                return web.json_response(json.loads(saved[0]))
            result = await tools.invoke(e, sid, required(body, "name"), body.get("arguments", {}))
            if body.get("request_id"):
                e.db.sql("INSERT INTO meta VALUES(?,?)", (key, json.dumps(result)))
            return web.json_response(result)

    @routes.post("/api/session/{sid}/chat")
    async def chat(request):
        sid = request.match_info["sid"]
        e.check_active(sid)
        body = await request.json()
        if any(not task.done() for task in e.tasks):
            raise UserError("A request is already running; wait or cancel it")
        if not e.caps:
            raise UserError("Gateway is unavailable")
        if not str(body.get("text", "")).strip():
            raise UserError("Enter a message or inspection requirement")
        for ident in body.get("images", []):
            assets.resolve(e.db, sid, ident)
        item = create(e.db, sid, "chat", {"text": body["text"], "images": body.get("images", []),
            "intent": body.get("intent", "chat"),
            "settings": e.db.session(sid)["settings"], "status": "queued"})
        e.spawn(chat_worker.scheduled(e, sid, item["id"]))
        return web.json_response(item)

    @routes.post("/api/session/{sid}/upload")
    async def upload(request):
        sid = request.match_info["sid"]
        e.check_active(sid)
        reader = await request.multipart()
        part = await reader.next()
        if not part or part.name != "image":
            raise UserError("Upload an image field")
        content = await part.read()
        image = await asyncio.to_thread(assets.decode, content, upload=not request.query.get("mask"))
        item = assets.save(e.db, sid, image, "mask" if request.query.get("mask") else "upload",
                           original_name=part.filename)
        return web.json_response(item)
