from .errors import json_body
from .errors import UserError, required
from aiohttp import web
from . import assets, sharing
from .records import get, update, create
from .settings import DATA


def install(routes, e):
    @routes.get("/api/session/{sid}/image/{ident}")
    async def image(request):
        sid, ident = request.match_info["sid"], int(request.match_info["ident"])
        e.check_active(sid)
        value = assets.resolve(e.db, sid, ident)
        headers = {"Cache-Control": "public, max-age=31536000, immutable"}
        if request.query.get("download"):
            headers["Content-Disposition"] = f'attachment; filename="image-{ident}.png"'
        if request.query.get("thumb"):
            return web.FileResponse(DATA / "thumbs" / value["thumb"], headers=headers)
        if value.get("file"):
            return web.FileResponse(DATA / "assets" / value["file"], headers=headers)
        return web.Response(body=assets.png(await assets.load(e.db, e.comfy, sid, ident)),
                            content_type="image/png", headers=headers)

    @routes.post("/api/session/{sid}/images")
    async def action(request):
        sid = request.match_info["sid"]
        e.check_active(sid)
        body = await json_body(request)
        ids, action = required(body, "ids"), required(body, "action")
        if not isinstance(ids, list) or any(type(i) is not int for i in ids):
            raise UserError("Image IDs must be a list of integers")
        if action in ("share", "revoke"):
            sharing.grant(e.db, sid, ids, action == "share")
        elif action == "final":
            if any(type(i) is not int or i > 10000 for i in ids):
                raise UserError("Only local images can be marked final")
            for ident in ids:
                get(e.db, sid, ident, "image")
            for ident in ids:
                update(e.db, sid, ident, final=bool(body.get("value", True)))
                create(e.db, sid, "event", {"image": ident, "action": "final" if body.get("value", True) else "draft"})
        elif action == "delete":
            if e.tasks:
                raise UserError("Finish active work before deleting images")
            for ident in ids:
                if ident > 10000:
                    raise UserError("Shared images are read-only")
                get(e.db, sid, ident, "image")
            for ident in ids:
                value = get(e.db, sid, ident)
                sharing.grant(e.db, sid, [ident], False)
                for key, folder in (("file", "assets"), ("thumb", "thumbs")):
                    if key in value:
                        (DATA / folder / value[key]).unlink(missing_ok=True)
                update(e.db, sid, ident, deleted=True)
        elif action == "export":
            from .export_images import export
            return await export(e, sid, ids)
        else:
            raise UserError("Unknown image action")
        return web.json_response({"ok": True})
