import asyncio
from aiohttp import web
from .run_worker import queue


def install(routes,e):
    @routes.get('/api/debug/runs/{id}')
    async def run(request):
        return web.json_response(e.db.get('runs',request.match_info['id']))

    @routes.get('/api/debug/system')
    async def system(request):
        results=await asyncio.gather(e.comfy.request('/llm/status'),
            e.comfy.request('/system_stats'),return_exceptions=True)
        return web.json_response({'queue':queue(e),'connections':{
            'engine':not e.error,'message':e.error,'events':e.comfy.events.ready.is_set()},
            'models':results[0] if not isinstance(results[0],Exception) else {'error':str(results[0])},
            'system':results[1] if not isinstance(results[1],Exception) else {'error':str(results[1])}})
