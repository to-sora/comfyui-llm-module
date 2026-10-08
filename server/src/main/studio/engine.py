import asyncio
import logging
from collections import defaultdict
from ..comfy import Comfy
from ..discovery import discover
from .store import Store, encode
from .migrate_backfill import backfill
from .events import Events
from .connection_status import message


class Stopped(Exception):
    pass


class Engine:
    def __init__(self):
        self.db = Store()
        self.events = Events(self.db)
        self.comfy = Comfy()
        self.comfy.on_status = self.connection
        self.caps, self.error = None, 'Connecting to the image engine'
        self.wake = asyncio.Event()
        self.prompts = defaultdict(set)
        self.previews = {}
        self.worker = None
        self.migrated = False

    async def start(self):
        await self.comfy.start()
        from .migrate import migrate
        await migrate(self.db, self.comfy)
        self.migrated = True
        if self.comfy.events.ready.is_set():
            await backfill(self.db,self.comfy)
        from .run_worker import recover, worker
        await recover(self)
        self.worker = asyncio.create_task(worker(self))
        self.wake.set()

    async def connection(self, ready, error):
        self.error = None if ready else error
        if ready:
            try:
                self.caps = await discover(self.comfy)
                if self.migrated:
                    await backfill(self.db,self.comfy)
            except Exception as exc:
                logging.exception('Image model discovery failed')
                self.error = str(exc) or 'Image model discovery failed'
        self.events.publish('*', 'system.status', {'connected':ready and not self.error,
            'message':message(self) or 'Ready'})

    def publish(self, run, kind, data):
        self.events.publish(run['chat_id'], kind, {'run_id':run['id'], **data})

    def trace(self, run, kind, data):
        current = self.db.get('runs', run['id'])['trace']
        current.setdefault('steps', []).append({'kind':kind, **data})
        self.db.update('runs', run['id'], trace_json=encode(current))
        self.publish(run, 'trace.changed', {})

    def check(self, run):
        if self.db.get('runs', run['id'])['cancelled']:
            raise Stopped('Stopped by the user')

    async def cancel(self, ident):
        from .cancel import cancel
        return await cancel(self,ident)

    async def close(self):
        for run in self.db.all("SELECT id FROM runs WHERE status IN ('queued','running')"):
            await self.cancel(run['id'])
        if self.worker:
            self.worker.cancel()
            await asyncio.gather(self.worker, return_exceptions=True)
        await self.comfy.close()
        self.db.db.close()
