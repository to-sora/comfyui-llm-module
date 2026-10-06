import io
import json
import zipfile
from aiohttp import web
from . import assets


async def export(e, sid, ids):
    stream = io.BytesIO()
    manifest = []
    with zipfile.ZipFile(stream, "w", zipfile.ZIP_DEFLATED) as archive:
        for ident in ids:
            value = assets.resolve(e.db, sid, ident)
            archive.writestr(f"image-{ident}.png", assets.png(await assets.load(e.db, e.comfy, sid, ident)))
            manifest.append(value)
        archive.writestr("images.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    return web.Response(body=stream.getvalue(), content_type="application/zip")
