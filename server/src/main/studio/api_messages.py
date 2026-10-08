from aiohttp import web
from ..errors import json_body,UserError
from . import chat_store
from .catalog import settings
from .image_store import metadata
from .message_api_data import page,preferences
from .run_worker import notify


def enqueue(e,chat,text,images):
    if not isinstance(text,str) or len(text)>100000:
        raise UserError('Use a message of at most 100,000 characters')
    if not isinstance(images,list) or len(images)>8 or any(not isinstance(i,str) for i in images):
        raise UserError('Attach up to eight images')
    if not text.strip() and not images:
        raise UserError('Write a message or attach a picture')
    for ident in images:
        if not metadata(e.db,ident)['file']:
            raise UserError('Wait for the attached image to finish')
    if e.db.one("SELECT id FROM runs WHERE chat_id=? AND status IN ('queued','running')",(chat,)):
        raise UserError('Wait for this chat’s reply, or stop it first')
    config={**preferences(e).get('assistant',{}),**e.db.get('chats',chat)['settings']}
    value=chat_store.turn(e.db,chat,text,images,settings(e.caps,config))
    e.events.publish(chat,'message.updated',value)
    e.events.publish('*','chats.changed',{'chat_id':chat})
    notify(e)
    e.wake.set()
    return value


def install(routes,e):
    @routes.get('/api/chats/{id}/messages')
    async def messages(request):
        chat=request.match_info['id']
        e.db.get('chats',chat)
        return web.json_response(page(e,chat,request.query.get('before')))

    @routes.post('/api/chats/{id}/messages')
    async def send(request):
        body=await json_body(request)
        return web.json_response(enqueue(e,request.match_info['id'],body.get('text',''),body.get('attachments',[])))

    @routes.post('/api/runs/{id}/cancel')
    async def cancel(request):
        await e.cancel(request.match_info['id'])
        return web.json_response({'ok':True})

    @routes.post('/api/runs/{id}/retry')
    async def retry(request):
        run=e.db.get('runs',request.match_info['id'])
        if run['status'] not in ('failed','cancelled','interrupted'):
            raise UserError('Only an unfinished reply can be retried')
        row=e.db.get('messages',run['message_id'])
        text='\n'.join(p['text'] for p in row['parts'] if p['type']=='text')
        images=[i for p in row['parts'] if p['type']=='images' for i in p['images']]
        return web.json_response(enqueue(e,run['chat_id'],text,images))
