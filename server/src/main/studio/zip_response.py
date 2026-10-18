import asyncio
import tempfile
import zipfile
from pathlib import Path
from aiohttp import web
from ..settings import DATA


async def send(request, name, files, texts=None):
    with tempfile.NamedTemporaryFile(dir=DATA/'tmp',suffix='.zip',delete=False) as f:
        path=Path(f.name)
    def write():
        with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_STORED) as archive:
            for filename,text in (texts or {}).items():
                archive.writestr(filename,text)
            for filename,source in files:
                if source.is_file():
                    archive.write(source,filename)
    try:
        await asyncio.to_thread(write)
        response=web.StreamResponse(headers={'Content-Type':'application/zip',
            'Content-Disposition':f'attachment; filename="{name}"',
            'Content-Length':str(path.stat().st_size)})
        await response.prepare(request)
        with path.open('rb') as stream:
            while chunk:=await asyncio.to_thread(stream.read,256*1024):
                await response.write(chunk)
        await response.write_eof()
        return response
    finally:
        path.unlink(missing_ok=True)
