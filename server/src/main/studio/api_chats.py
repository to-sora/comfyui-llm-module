from aiohttp import web
from ..errors import UserError,json_body
from . import chat_store
from .store import encode


def install(routes,e):
    @routes.get('/api/chats')
    async def listing(request):
        rows=e.db.all('''SELECT c.*,EXISTS(SELECT 1 FROM runs r WHERE r.chat_id=c.id
            AND r.status IN ('queued','running')) AS running FROM chats c
            WHERE c.archived=? ORDER BY c.pinned DESC,c.updated DESC''',(int(request.query.get('archived')=='1'),))
        return web.json_response({'chats':rows})

    @routes.post('/api/chats')
    async def create(request):
        value=chat_store.create(e.db)
        e.events.publish('*','chats.changed',{'chat_id':value['id']})
        return web.json_response(value)

    @routes.get('/api/chats/{id}')
    async def get(request):
        return web.json_response(e.db.get('chats',request.match_info['id']))

    @routes.patch('/api/chats/{id}')
    async def patch(request):
        ident=request.match_info['id']
        e.db.get('chats',ident)
        body=await json_body(request)
        updates={}
        if 'title' in body:
            title=body['title']
            if not isinstance(title,str) or not title.strip() or len(title)>100:
                raise UserError('Choose a title between 1 and 100 characters')
            updates['title']=title.strip()
        for name in ('pinned','archived'):
            if name in body:
                if type(body[name]) is not bool:
                    raise UserError('Choose a boolean for '+name)
                updates[name]=int(body[name])
        if not updates:
            raise UserError('Choose a title, pin or archive change')
        value=e.db.update('chats',ident,**updates)
        e.events.publish('*','chats.changed',{'chat_id':ident})
        return web.json_response(value)

    @routes.delete('/api/chats/{id}')
    async def delete(request):
        ident=request.match_info['id']
        e.db.get('chats',ident)
        if e.db.one("SELECT id FROM runs WHERE chat_id=? AND status IN ('queued','running')",(ident,)):
            raise UserError('Stop this chat’s reply before deleting it')
        chat_store.remove(e.db,ident)
        e.events.publish('*','chats.changed',{'chat_id':ident})
        return web.json_response({'ok':True})

    @routes.get('/api/chats/{id}/events')
    async def events(request):
        ident=request.match_info['id']
        e.db.get('chats',ident)
        return await e.events.stream(request,ident)

    @routes.get('/api/events')
    async def global_events(request):
        return await e.events.stream(request,'*')
