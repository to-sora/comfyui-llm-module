import asyncio
import shutil
import zipfile
from ..settings import DATA
from ..errors import UserError
from .backup_data import read,merge


async def restore(e,path):
    def unpack():
        with zipfile.ZipFile(path) as archive:
            data=read(archive)
            total=sum(i.file_size for i in archive.infolist())
            if total>20*1024**3 or total>shutil.disk_usage(DATA).free-2*1024**3:
                raise UserError('There is not enough storage for this backup')
            for info in archive.infolist():
                if info.filename=='studio.json':
                    continue
                target=DATA/info.filename
                target.parent.mkdir(exist_ok=True)
                if target.exists():
                    continue
                staging=target.with_name(target.name+'.restore')
                try:
                    with archive.open(info) as source,staging.open('wb') as out:
                        shutil.copyfileobj(source,out,256*1024)
                    staging.replace(target)
                finally:
                    staging.unlink(missing_ok=True)
        return data
    data=await asyncio.to_thread(unpack)
    counts=merge(e.db,data)
    e.events.publish('*','chats.changed',{'restored':True})
    return {'restored':counts,'mode':'merge; existing records and files are kept'}
