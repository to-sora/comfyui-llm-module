from aiohttp import web
from ..errors import UserError,json_body
from ..settings import DATA
from .image_store import metadata
from .image_downloads import archive


def install(routes,e):
    @routes.get('/api/images')
    async def listing(request):
        where="deleted=0 AND kind!='mask' AND file IS NOT NULL AND id<?"
        if request.query.get('filter')=='favorites':
            where+=' AND favorite=1'
        rows=e.db.all('SELECT * FROM images WHERE '+where+' ORDER BY id DESC LIMIT 60',
                      (request.query.get('cursor','Z'),))
        return web.json_response({'images':rows,'cursor':rows[-1]['id'] if len(rows)==60 else None})

    @routes.patch('/api/images/{id}')
    async def favorite(request):
        ident=request.match_info['id']
        metadata(e.db,ident)
        body=await json_body(request)
        if type(body.get('favorite')) is not bool:
            raise UserError('Choose whether to favorite this image')
        return web.json_response(e.db.update('images',ident,favorite=int(body['favorite'])))

    @routes.post('/api/images/actions')
    async def action(request):
        body=await json_body(request)
        ids=body.get('images')
        if not isinstance(ids,list) or not 1<=len(ids)<=200 or any(not isinstance(i,str) for i in ids):
            raise UserError('Select between 1 and 200 images')
        rows=[metadata(e.db,i) for i in dict.fromkeys(ids)]
        if body.get('action')=='download':
            return await archive(e,request,[r['id'] for r in rows])
        if body.get('action')!='delete':
            raise UserError('Choose download or delete')
        if e.db.one("SELECT id FROM runs WHERE status IN ('running','queued')"):
            raise UserError('Wait for queued replies to finish before deleting images')
        with e.db.transaction():
            for row in rows:
                e.db.update('images',row['id'],deleted=1)
        for row in rows:
            for folder,key in (('assets','file'),('thumbs','thumb')):
                if row[key] and not e.db.one(f'SELECT id FROM images WHERE deleted=0 AND {key}=?',(row[key],)):
                    (DATA/folder/row[key]).unlink(missing_ok=True)
            for folder,ext in (('vision','.jpg'),('cache','.jpg')):
                (DATA/folder/(row['id']+ext)).unlink(missing_ok=True)
            e.previews.pop(row['id'],None)
        return web.json_response({'deleted':[r['id'] for r in rows]})
