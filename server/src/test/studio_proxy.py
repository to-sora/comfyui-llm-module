import asyncio
import socket
import ssl
import threading
import aiohttp
from aiohttp import web
from studio_helpers import ROOT
from studio_proxy_routes import relay


class Proxy:
    """A real HTTPS relay; disconnect only this test browser, keeping the harness running."""
    def __init__(self):
        self.loop=asyncio.new_event_loop()
        self.thread=threading.Thread(target=self.loop.run_forever,daemon=True)
        self.transports=set()
        self.blocked=False
        self.resumed=[]

    def invoke(self,job):
        return asyncio.run_coroutine_threadsafe(job,self.loop).result(10)

    async def forward(self,request):
        return await relay(self,request)

    async def start(self):
        self.client=aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False,family=socket.AF_INET),
                                          timeout=aiohttp.ClientTimeout(total=None))
        app=web.Application()
        app.router.add_route('*','/{tail:.*}',self.forward)
        self.runner=web.AppRunner(app,shutdown_timeout=1,handler_cancellation=True)
        await self.runner.setup()
        tls=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        tls.load_cert_chain(ROOT/'server/data/tls/cert.pem',ROOT/'server/data/tls/key.pem')
        site=web.TCPSite(self.runner,'0.0.0.0',0,ssl_context=tls)
        await site.start()
        return 'https://127.0.0.1:'+str(site._server.sockets[0].getsockname()[1])

    async def outage(self,blocked):
        self.blocked=blocked
        if blocked:
            for transport in list(self.transports): transport.abort()

    async def close(self):
        await self.outage(True)
        await self.client.close()
        await self.runner.cleanup()
        tasks=asyncio.all_tasks()-{asyncio.current_task()}
        for task in tasks: task.cancel()
        await asyncio.gather(*tasks,return_exceptions=True)

    def __enter__(self):
        self.thread.start();self.url=self.invoke(self.start());return self

    def __exit__(self,*args):
        self.invoke(self.close());self.loop.call_soon_threadsafe(self.loop.stop);self.thread.join(5)
        self.loop.close()
