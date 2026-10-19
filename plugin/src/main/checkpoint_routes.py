from aiohttp import web
from .errors import json_body, message
from . import ram_budget
from .checkpoint_lifetime import TURNS, CHECKPOINTS, release, snapshot
from .checkpoint_cache import path_for


def reserve(token, names):
    if not isinstance(names,list) or len(names)>8 or any(not isinstance(n,str) for n in names):
        raise ValueError('checkpoints must contain up to eight available model names')
    paths = {str(path_for(name)) for name in names}
    with ram_budget.LOCK:
        all_paths = paths | {p for t in TURNS.values() for p in t['sources']}
        from pathlib import Path
        if sum(Path(p).stat().st_size for p in all_paths)>ram_budget.SDXL_LIMIT:
            raise MemoryError('Active turns exceed the 16 GB SDXL RAM budget; finish a turn first')
        turn = TURNS.setdefault(token,{'sources':set(),'entries':{}})
        turn['sources'].update(paths)
        for path in paths:
            entry = CHECKPOINTS.get(path)
            if entry is not None:
                turn['entries'][path] = entry


def install(routes):
    @routes.put('/llm/turns/{token}')
    async def begin(request):
        try:
            body = await json_body(request)
            reserve(request.match_info['token'],body.get('checkpoints',[]))
            return web.json_response(snapshot())
        except (ValueError,MemoryError) as exc:
            return web.json_response({'error':message(exc)},status=409)

    @routes.delete('/llm/turns/{token}')
    async def end(request):
        release(request.match_info['token'])
        return web.json_response(snapshot())
