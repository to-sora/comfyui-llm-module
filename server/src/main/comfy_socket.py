import asyncio
import json
import logging
import aiohttp
from .comfy_preview import decode


async def status(events, ready):
    callback = getattr(events.comfy, 'on_status', None)
    if callback:
        try:
            await callback(ready, events.failure if not ready else None)
        except Exception:
            logging.exception('ComfyUI connection status update failed')


async def listen(events):
    delay = .5
    while True:
        try:
            async with events.comfy.client.ws_connect(events.comfy.url+'/ws',
                    params={'clientId':events.client_id}, heartbeat=20) as ws:
                events.ready.set()
                events.failure = None
                delay = .5
                await status(events, True)
                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        await events.dispatch(json.loads(msg.data))
                    elif msg.type == aiohttp.WSMsgType.BINARY:
                        value = decode(msg.data, events.active)
                        if value:
                            await events.dispatch(value)
                raise ConnectionError('ComfyUI event connection closed')
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logging.exception('ComfyUI event connection failed')
            events.failure = str(exc).strip() or 'ComfyUI event connection failed'
            events.ready.clear()
            for future, _ in list(events.pending.values()):
                if not future.done():
                    future.set_exception(ConnectionError(events.failure))
            await status(events, False)
            await asyncio.sleep(delay)
            delay = min(delay*2, 30)
