"""Extension-owned worker-to-gateway events; no ComfyUI internals replaced."""
import asyncio
import threading

STREAMS={}
LOCK=threading.RLock()


def register(ident,callback,future):
    if callback:
        with LOCK:
            STREAMS[ident]=(asyncio.get_running_loop(),callback,future)


def remove(ident):
    with LOCK:
        STREAMS.pop(ident,None)


def emit(ident,delta):
    with LOCK:
        target=STREAMS.get(ident)
    if not target:
        return
    loop,callback,future=target
    async def deliver():
        try:
            await callback({'type':'llm.token','data':{'prompt_id':ident,'delta':delta}})
        except Exception as exc:
            if not future.done():
                future.set_exception(exc)
    loop.call_soon_threadsafe(lambda:asyncio.create_task(deliver()))
