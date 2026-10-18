import time
from aiohttp import web
from ..errors import UserError,json_body
from ..settings import DATA


def install(routes,e):
    @routes.get('/api/storage')
    async def storage(request):
        row=e.db.one('SELECT COUNT(*) AS images,COALESCE(SUM(bytes),0) AS bytes FROM images WHERE deleted=0')
        folders={}
        for folder in ('assets','thumbs','vision','documents'):
            folders[folder]=sum(p.stat().st_size for p in (DATA/folder).glob('*') if p.is_file())
        row.update(folders=folders,total_bytes=sum(folders.values()),database_bytes=(DATA/'studio.sqlite').stat().st_size)
        return web.json_response(row)

    @routes.get('/api/storage/candidates')
    async def candidates(request):
        try:
            days=max(1,min(3650,int(request.query.get('days','30'))))
        except ValueError as exc:
            raise UserError('Choose an age in days') from exc
        rows=e.db.all('''SELECT id,bytes,created,chat_id,thumb FROM images WHERE deleted=0 AND favorite=0
            AND file IS NOT NULL AND created<? ORDER BY created LIMIT 200''',(time.time()-days*86400,))
        return web.json_response({'images':rows,'bytes':sum(r['bytes'] or 0 for r in rows)})
