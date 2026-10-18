from pathlib import Path
import time
from aiohttp import web
from ..settings import DATA
from ..errors import UserError
from .ids import new
from .documents import extract,get


def install(routes,e):
    @routes.post('/api/documents')
    async def upload(request):
        reader=await request.multipart()
        field=await reader.next()
        if not field or field.name!='file':
            raise UserError('Choose a PDF or text document')
        name=Path(field.filename or 'document.txt').name[:200]
        suffix=Path(name).suffix.lower()
        if suffix not in ('.pdf','.txt','.md','.csv','.json','.log'):
            raise UserError('Choose PDF, text, Markdown, CSV or JSON')
        ident=new()
        folder=DATA/'documents'
        folder.mkdir(exist_ok=True)
        path=folder/(ident+suffix)
        size=0
        try:
            with path.open('wb') as target:
                while chunk:=await field.read_chunk():
                    size+=len(chunk)
                    if size>10*1024**2:
                        raise UserError('Documents may be at most 10 MiB')
                    target.write(chunk)
            result=await extract(path)
            e.db.insert('documents',id=ident,name=name,file=path.name,text=result['text'],
                        bytes=size,created=time.time(),truncated=int(result['truncated']))
            return web.json_response({'id':ident,'name':name,'kind':'document','bytes':size,
                                      'characters':len(result['text']),'truncated':result['truncated']})
        except BaseException:
            path.unlink(missing_ok=True)
            raise

    @routes.get('/api/documents/{id}')
    async def download(request):
        item=get(e.db,request.match_info['id'])
        return web.FileResponse(DATA/'documents'/item['file'],headers={
            'Content-Disposition':'attachment; filename="'+item['id']+Path(item['file']).suffix+'"'})
