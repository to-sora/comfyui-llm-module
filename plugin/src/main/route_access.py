from aiohttp import web
from .network import port_config


class Routes:
    def __init__(self,routes):
        self.routes=routes
        self.config=port_config()

    def route(self,method,path):
        def decorate(handler):
            async def guarded(request):
                if self.config['enable_whitelist'] and request.remote not in self.config['allowed']:
                    raise web.HTTPForbidden()
                return await handler(request)
            return getattr(self.routes,method)(path)(guarded)
        return decorate

    def get(self,path):
        return self.route('get',path)

    def post(self,path):
        return self.route('post',path)

    def put(self,path):
        return self.route('put',path)

    def delete(self,path):
        return self.route('delete',path)
