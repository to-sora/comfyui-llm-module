from aiohttp import web
from ..errors import UserError,json_body
from .catalog import settings,styles
from .message_api_data import preferences
from .store import encode
from .run_worker import queue


def install(routes,e):
    @routes.get('/api/bootstrap')
    async def bootstrap(request):
        cursor=e.db.one('SELECT COALESCE(MAX(seq),0) AS n FROM events')['n']
        return web.json_response({'connected':bool(e.caps) and not e.error,'error':e.error,
            'profiles':(e.caps or {}).get('profiles',[]),'styles':styles(e.caps) if e.caps else {},
            'checkpoints':(e.caps or {}).get('checkpoints',[]),
            'settings':preferences(e),'assistant':settings(e.caps,preferences(e).get('assistant')),
            'cursor':cursor,'queue':queue(e)})

    @routes.put('/api/settings')
    async def save(request):
        body=await json_body(request)
        if body.get('theme') not in ('system','light','dark') or body.get('language') not in ('en','zh-Hant','zh-Hans'):
            raise UserError('Choose a listed theme and language')
        value={k:body[k] for k in ('theme','language')}
        value['technical']=bool(body.get('technical'))
        value['assistant']=settings(e.caps,body.get('assistant'))
        if body.get('chat_id'):
            e.db.get('chats',body['chat_id'])
            e.db.update('chats',body['chat_id'],settings_json=encode(value['assistant']))
        e.db.db.execute("INSERT OR REPLACE INTO preferences VALUES('settings',?)",(encode(value),))
        return web.json_response(value)

    @routes.post('/api/reconnect')
    async def reconnect(request):
        await e.connection(e.comfy.events.ready.is_set(),e.comfy.events.failure)
        return web.json_response({'connected':bool(e.caps) and not e.error,'error':e.error})
