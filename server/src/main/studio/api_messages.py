from aiohttp import web
from ..errors import json_body,UserError
from . import chat_store
from .catalog import settings
from .image_store import metadata
from .message_api_data import page,preferences
from .run_worker import notify


from .message_enqueue import enqueue


def install(routes,e):
    @routes.get('/api/chats/{id}/messages')
    async def messages(request):
        chat=request.match_info['id']
        e.db.get('chats',chat)
        return web.json_response(page(e,chat,request.query.get('before')))

    @routes.post('/api/chats/{id}/messages')
    async def send(request):
        body=await json_body(request)
        return web.json_response(enqueue(e,request.match_info['id'],body.get('text',''),body.get('attachments',[]),body.get('parent_id',...),body.get('documents',[])))

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
        text='Please make a fresh attempt at this request:\n\n'+text
        docs=[i for p in row['parts'] if p['type']=='documents' for i in p['documents']]
        value=enqueue(e,run['chat_id'],text,images,documents=docs)
        e.trace(e.db.get('runs',value['run_id']),'retry',{'original_run':run['id']})
        return web.json_response(value)
