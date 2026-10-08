import asyncio
from aiohttp import web
from PIL import UnidentifiedImageError,Image
from ..assets import decode
from ..errors import UserError
from ..settings import read
from .image_store import reserve,save,metadata


def install(routes,e):
    @routes.post('/api/uploads')
    async def upload(request):
        reader=await request.multipart()
        field=await reader.next()
        if not field or field.name!='file':
            raise UserError('Choose an image to attach')
        raw=bytearray()
        while chunk:=await field.read_chunk():
            raw.extend(chunk)
            if len(raw)>read()['upload_mb']*1024**2:
                raise UserError('The image file is too large to upload')
        try:
            image=await asyncio.to_thread(decode,bytes(raw),True)
        except (UnidentifiedImageError,OSError,Image.DecompressionBombError) as exc:
            raise UserError('This image could not be read. Choose PNG, JPG, WebP or HEIC.') from exc
        kind='mask' if request.query.get('kind')=='mask' else 'upload'
        parents=[]
        if kind=='mask':
            source=metadata(e.db,request.query.get('source'))
            if image.size!=(source['width'],source['height']):
                raise UserError('The painted area must match its source image')
            parents=[source['id']]
        with e.db.transaction():
            ident=reserve(e.db,None,None,{'operation':'upload','name':(field.filename or 'Image')[:200]},parents,kind=kind)
            value=save(e.db,ident,image)
        return web.json_response(value)
