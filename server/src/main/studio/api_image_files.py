from aiohttp import web
from ..settings import DATA
from ..errors import UserError
from .image_store import metadata
from .image_downloads import jpeg


def install(routes,e):
    @routes.get('/api/images/{id}')
    async def image(request):
        ident=request.match_info['id']
        item=metadata(e.db,ident)
        if not item['file']:
            raise UserError('This image has not finished yet')
        fmt='jpg' if request.query.get('format')=='jpg' else 'png'
        headers={'Cache-Control':'public, max-age=31536000, immutable'}
        if 'download' in request.query:
            headers['Content-Disposition']=f'attachment; filename="studio-{ident}.{fmt}"'
        if fmt=='jpg':
            path=DATA/'cache'/(ident+'.jpg')
            if not path.is_file():
                path.write_bytes(jpeg(e,ident))
        else:
            path=DATA/'assets'/item['file']
        return web.FileResponse(path,headers=headers)

    @routes.get('/api/images/{id}/thumb')
    async def thumb(request):
        item=metadata(e.db,request.match_info['id'])
        if not item['thumb']:
            raise UserError('This image has not finished yet')
        return web.FileResponse(DATA/'thumbs'/item['thumb'],
            headers={'Cache-Control':'public, max-age=31536000, immutable'})

    @routes.get('/api/images/{id}/info')
    async def info(request):
        item=metadata(e.db,request.match_info['id'])
        family=e.db.all("SELECT id,parents_json,created,file,deleted FROM images WHERE deleted=0 AND kind!='mask'")
        related={item['id'],*item['parents']}
        changed=True
        while changed:
            before=len(related)
            for row in family:
                if row['id'] in related or set(row['parents']) & related:
                    related.update([row['id'],*row['parents']])
            changed=len(related)!=before
        item['versions']=[row for row in family if row['id'] in related and row['file']]
        return web.json_response(item)

    @routes.get('/api/previews/{id}')
    async def preview(request):
        value=e.previews.get(request.match_info['id'])
        if value is None:
            raise web.HTTPNotFound()
        return web.Response(body=value[0],content_type=value[1],headers={'Cache-Control':'no-store'})
