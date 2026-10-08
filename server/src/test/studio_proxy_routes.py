import asyncio
import aiohttp
from aiohttp import web


async def relay(proxy,request):
    if proxy.blocked:
        return web.json_response({'error':'Temporary test connection outage'},status=503)
    transport=request.transport
    proxy.transports.add(transport)
    cursor=request.headers.get('Last-Event-ID')
    if cursor: proxy.resumed.append(cursor)
    headers={k:v for k,v in request.headers.items() if k.lower() not in ('host','connection','content-length')}
    try:
        async with proxy.client.request(request.method,'https://127.0.0.1:8189'+str(request.rel_url),
                headers=headers,data=await request.read()) as upstream:
            response=web.StreamResponse(status=upstream.status,headers={k:v for k,v in upstream.headers.items()
                if k.lower() not in ('connection','transfer-encoding','content-length','content-encoding')})
            await response.prepare(request)
            async for chunk in upstream.content.iter_any():
                await response.write(chunk)
            return response
    except (ConnectionError,aiohttp.ClientError):
        if transport: transport.abort()
        return web.Response(status=503)
    finally:
        proxy.transports.discard(transport)
