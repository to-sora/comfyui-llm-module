import asyncio
import psutil
from aiohttp import web

JOBS=asyncio.Semaphore(2)


def admit():
    memory=psutil.virtual_memory()
    free=min(memory.available,max(0,80_000_000_000-memory.total+memory.available))
    if free<10*1024**3:
        raise web.HTTPServiceUnavailable(text='RAM reserve is low; wait for existing work to finish')


@web.middleware
async def guard(request,handler):
    write=request.method in ('POST','PUT','PATCH','DELETE')
    if write and getattr(request.app.get('engine'),'maintenance',False):
        return web.json_response({'error':'A backup or restore is in progress. Please wait.'},status=503)
    heavy=write and (request.path.startswith(('/api/uploads','/api/documents')) or request.path.endswith(('/edit','/outpaint')))
    if heavy or request.path.startswith('/api/images/') and request.query.get('format')=='jpg':
        async with JOBS:
            admit()
            return await handler(request)
    return await handler(request)
