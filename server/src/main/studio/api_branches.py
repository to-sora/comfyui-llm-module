from aiohttp import web
from ..errors import UserError,json_body
from .api_messages import enqueue
from .branches import select,idle
from .store import encode


def install(routes,e):
    @routes.post('/api/chats/{id}/branch')
    async def branch(request):
        body=await json_body(request)
        select(e,request.match_info['id'],body.get('tip'))
        return web.json_response({'ok':True})

    @routes.post('/api/messages/{id}/regenerate')
    async def regenerate(request):
        row=e.db.get('messages',request.match_info['id'])
        if row['role']=='assistant':
            if not row['run_id']:
                raise UserError('Use Quick edits to revise this local edit')
            row=e.db.get('messages',row['parent_id'])
        if row['role']!='user':
            raise UserError('Choose a user message or reply')
        text='\n'.join(p['text'] for p in row['parts'] if p['type']=='text')
        images=[i for p in row['parts'] if p['type']=='images' for i in p['images']]
        docs=[i for p in row['parts'] if p['type']=='documents' for i in p['documents']]
        return web.json_response(enqueue(e,row['chat_id'],text,images,row['parent_id'],docs))

    @routes.post('/api/messages/{id}/feedback')
    async def feedback(request):
        row=e.db.get('messages',request.match_info['id'])
        body=await json_body(request)
        if body.get('rating') not in ('up','down','clear'):
            raise UserError('Choose thumbs up or down')
        key='feedback:'+row['id']
        value={'rating':body['rating'],'note':str(body.get('note',''))[:2000]}
        e.db.db.execute('INSERT OR REPLACE INTO preferences VALUES(?,?)',(key,encode(value)))
        return web.json_response(value)

    @routes.post('/api/runs/{id}/resume')
    async def resume(request):
        from .resume import enqueue_resume
        return web.json_response(enqueue_resume(e,request.match_info['id']))
