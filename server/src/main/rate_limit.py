import time
from collections import OrderedDict
from aiohttp import web
from .settings import read

BUCKETS=OrderedDict()


@web.middleware
async def limit(request,handler):
    maximum=read().get('requests_per_minute',60)
    if maximum and (request.method in ('POST','PUT','PATCH','DELETE') or request.path in ('/api/backup','/api/storage')):
        now=time.monotonic()
        key=request.remote or 'unknown'
        count,previous=BUCKETS.pop(key,(float(maximum),now))
        count=min(maximum,count+(now-previous)*maximum/60)
        BUCKETS[key]=(max(0,count-1),now)
        while len(BUCKETS)>4096:
            BUCKETS.popitem(last=False)
        if count<1:
            return web.json_response({'error':'Too many requests. Please wait a moment.'},status=429,
                                     headers={'Retry-After':str(max(1,int(60/maximum)))})
    return await handler(request)
