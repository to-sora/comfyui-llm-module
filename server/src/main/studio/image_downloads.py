import io
import tempfile
import zipfile
from pathlib import Path
from PIL import Image
from aiohttp import web
from ..settings import DATA
from .image_store import load,metadata


def jpeg(e,ident):
    image=load(e.db,ident)
    canvas=Image.new('RGB',image.size,'white')
    canvas.paste(image,mask=image.getchannel('A'))
    buffer=io.BytesIO()
    canvas.save(buffer,format='JPEG',quality=95)
    return buffer.getvalue()


async def archive(e,request,ids):
    with tempfile.NamedTemporaryFile(dir=DATA/'tmp',suffix='.zip',delete=False) as temp:
        path=Path(temp.name)
    try:
        with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_STORED) as target:
            for ident in ids:
                item=metadata(e.db,ident)
                if item['file']:
                    target.write(DATA/'assets'/item['file'],ident+'.png')
        response=web.StreamResponse(headers={'Content-Type':'application/zip',
            'Content-Disposition':'attachment; filename="studio-images.zip"',
            'Content-Length':str(path.stat().st_size)})
        await response.prepare(request)
        with path.open('rb') as source:
            while chunk:=source.read(1024*256):
                await response.write(chunk)
        await response.write_eof()
        return response
    finally:
        path.unlink(missing_ok=True)
