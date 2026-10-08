import asyncio
import json
import time
from collections import defaultdict
from aiohttp import web
from .store import encode


class Events:
    def __init__(self, store):
        self.store = store
        self.watchers = defaultdict(set)

    def publish(self, chat, kind, data):
        self.store.insert('events', chat_id=chat, kind=kind, data_json=encode(data), created=time.time())
        global_events=self.watchers['*'] if kind in ('chats.changed','queue.changed','system.status') else set()
        for event in self.watchers[chat] | global_events:
            event.set()

    async def stream(self, request, chat):
        raw = request.headers.get('Last-Event-ID', request.query.get('cursor', '0'))
        try:
            cursor = max(0, int(raw))
        except ValueError:
            raise web.HTTPBadRequest(text='Invalid event cursor')
        response = web.StreamResponse(headers={'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache'})
        await response.prepare(request)
        await response.write(b': connected\n\n')
        wake = asyncio.Event()
        self.watchers[chat].add(wake)
        try:
            while request.transport and not request.transport.is_closing():
                wake.clear()
                if chat == '*':
                    rows = self.store.all("SELECT * FROM events WHERE seq>? AND kind IN ('chats.changed','queue.changed','system.status') ORDER BY seq LIMIT 200", (cursor,))
                else:
                    rows = self.store.all('SELECT * FROM events WHERE seq>? AND chat_id=? ORDER BY seq LIMIT 200', (cursor, chat))
                for row in rows:
                    cursor = row['seq']
                    value = f'id: {cursor}\nevent: {row["kind"]}\ndata: {encode(row["data"])}\n\n'
                    await response.write(value.encode())
                if len(rows) == 200:
                    continue
                try:
                    await asyncio.wait_for(wake.wait(), 15)
                except TimeoutError:
                    await response.write(b': connected\n\n')
        except (ConnectionError, asyncio.CancelledError):
            pass
        finally:
            self.watchers[chat].discard(wake)
        return response
