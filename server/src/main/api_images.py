import io
import json
import zipfile
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
        raw = (DATA / "thumbs" / value["thumb"]).read_bytes() if request.query.get("thumb") else assets.png(
            await assets.load(e.db, e.comfy, sid, ident))
        headers = {"Cache-Control": "no-store"}
        if request.query.get("download"):
            headers["Content-Disposition"] = f'attachment; filename="image-{ident}.png"'
        return web.Response(body=raw, content_type="image/png", headers=headers)

    @routes.post("/api/session/{sid}/images")
    async def action(request):
        sid = request.match_info["sid"]
        e.check_active(sid)
        body = await request.json()
        ids, action = body["ids"], body["action"]
        if action in ("share", "revoke"):
            sharing.grant(e.db, sid, ids, action == "share")
        elif action == "final":
            for ident in ids:
                get(e.db, sid, ident, "image")
                update(e.db, sid, ident, final=bool(body.get("value", True)))
                create(e.db, sid, "event", {"image": ident, "action": "final" if body.get("value", True) else "draft"})
        elif action == "delete":
            if e.tasks:
                raise ValueError("Finish active work before deleting images")
            for ident in ids:
                if ident > 10000:
                    raise ValueError("Shared images are read-only")
                get(e.db, sid, ident, "image")
            for ident in ids:
                value = get(e.db, sid, ident)
                sharing.grant(e.db, sid, [ident], False)
                for key, folder in (("file", "assets"), ("thumb", "thumbs")):
                    if key in value:
                        (DATA / folder / value[key]).unlink(missing_ok=True)
                update(e.db, sid, ident, deleted=True)
        elif action == "export":
            stream = io.BytesIO()
            manifest = []
            with zipfile.ZipFile(stream, "w", zipfile.ZIP_DEFLATED) as archive:
                for ident in ids:
                    value = assets.resolve(e.db, sid, ident)
                    archive.writestr(f"image-{ident}.png", assets.png(await assets.load(e.db, e.comfy, sid, ident)))
                    manifest.append(value)
                archive.writestr("images.json", json.dumps(manifest, ensure_ascii=False, indent=2))
            return web.Response(body=stream.getvalue(), content_type="application/zip")
        else:
            raise ValueError("Unknown image action")
        return web.json_response({"ok": True})
