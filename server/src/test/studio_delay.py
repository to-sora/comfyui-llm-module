import asyncio
import subprocess
from aiohttp import web
from studio_proxy import Proxy
from studio_helpers import ROOT


class Delayed(Proxy):
    """Real API relay, optionally replaying a prior committed browser implementation."""
    def __init__(self, delays, source_ref=None):
        super().__init__()
        self.delays,self.source_ref = delays,source_ref
        self.done,self.posts = [],[]
        self.sources = {}

    async def forward(self, request):
        path = request.path
        key = (request.method,path)
        if request.method=='POST':
            self.posts.append(path)
        if key in self.delays:
            await asyncio.sleep(self.delays[key])
        source = None
        if self.source_ref and request.method=='GET':
            if path=='/' or path.startswith('/chats/'):
                source='index.html'
            elif path.startswith('/static/') and path[8:] in (
                    'main.js','composer.js','state.js','uploads.js','chats.js',
                    'library.js','viewer_detail.js','mask.js'):
                source=path[8:]
        if source:
            if source not in self.sources:
                self.sources[source]=subprocess.check_output(['git','show',
                    self.source_ref+':server/web-studio/'+source],cwd=ROOT)
            result=web.Response(body=self.sources[source],
                content_type='text/html' if source.endswith('.html') else 'text/javascript')
        else:
            result=await super().forward(request)
        if key in self.delays:
            self.done.append(key)
        return result
