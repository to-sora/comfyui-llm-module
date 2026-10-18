import asyncio
import tempfile
import shutil
from pathlib import Path
from aiohttp import web
from ..settings import DATA
from ..errors import UserError
from .backup_data import manifest,FOLDERS
from .store import encode
from .zip_response import send


def idle(e):
    if getattr(e,'maintenance',False) or e.db.one("SELECT id FROM runs WHERE status IN ('queued','running')"):
        raise UserError('Finish or stop queued replies before backing up or restoring')


def install(routes,e):
    @routes.get('/api/backup')
    async def backup(request):
        idle(e)
        e.maintenance=True
        try:
            data=encode(manifest(e.db))
            if len(data.encode())>64*1024**2:
                raise UserError('Backup metadata exceeds the 64 MiB limit')
            files=[(folder+'/'+p.name,p) for folder in FOLDERS for p in (DATA/folder).glob('*') if p.is_file()]
            total=sum(p.stat().st_size for _,p in files)
            if total>shutil.disk_usage(DATA).free-2*1024**3:
                raise UserError('Not enough free storage to prepare the backup')
            return await send(request,'studio-backup.zip',files,{'studio.json':data})
        finally:
            e.maintenance=False

    @routes.post('/api/backup/restore')
    async def restore(request):
        from .backup_restore import restore as apply
        idle(e)
        e.maintenance=True
        path=None
        try:
            reader=await request.multipart()
            field=await reader.next()
            if not field or field.name!='file':
                raise UserError('Choose a Studio backup ZIP')
            limit=min(20*1024**3,shutil.disk_usage(DATA).free-2*1024**3)
            size=0
            with tempfile.NamedTemporaryFile(dir=DATA/'tmp',suffix='.zip',delete=False) as out:
                path=Path(out.name)
                while chunk:=await field.read_chunk(256*1024):
                    size+=len(chunk)
                    if size>limit:
                        raise UserError('The backup exceeds the available restore space')
                    await asyncio.to_thread(out.write,chunk)
            return web.json_response(await apply(e,path))
        finally:
            if path:
                path.unlink(missing_ok=True)
            e.maintenance=False
