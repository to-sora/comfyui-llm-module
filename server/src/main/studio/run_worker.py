import asyncio
import logging
import time
from .run_error import mark_images
from .engine import Stopped
from ..errors import UserError, message
from .run_result import finish


def queue(e):
    active = e.db.all("SELECT id,chat_id,status FROM runs WHERE status='running' ORDER BY id")
    waiting = e.db.all("SELECT id,chat_id,status FROM runs WHERE status='queued' ORDER BY id")
    return {'active':active,'waiting':[dict(row,position=i+1) for i,row in enumerate(waiting)]}


def notify(e):
    value = queue(e)
    e.events.publish('*', 'queue.changed', value)
    for row in value['active']+value['waiting']:
        e.events.publish(row['chat_id'], 'run.queued', row)


def plain(exc):
    text=message(exc)
    if isinstance(exc, UserError):
        return text
    if 'out of memory' in text.lower():
        return 'Ran out of GPU memory. Try fewer images or a smaller size.'
    if isinstance(exc, (ConnectionError, TimeoutError)) or 'connect' in text.lower():
        return 'The image engine could not finish the request. Check its connection and try again.'
    return 'Something went wrong while making this reply. Try again; details are in Debug.'


async def recover(e):
    for run in e.db.all("SELECT * FROM runs WHERE status IN ('running','queued')"):
        for prompt in run['trace'].get('prompt_ids', []):
            try:
                await e.comfy.cancel(prompt)
            except Exception:
                logging.exception('Could not cancel an interrupted prompt')
        e.db.update('runs',run['id'],status='interrupted',finished=time.time(),
                    error='This request was interrupted by a restart. Try again to continue.')


async def worker(e):
    from .agent import run as generate
    while True:
        e.wake.clear()
        job = e.db.one("SELECT * FROM runs WHERE status='queued' ORDER BY id LIMIT 1")
        if not job:
            await e.wake.wait()
            continue
        try:
            e.check(job)
            e.db.update('runs',job['id'],status='running',started=time.time())
            notify(e)
            await generate(e,job)
            e.check(job)
            finish(e,job)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            stopped = isinstance(exc,Stopped) or e.db.get('runs',job['id'])['cancelled']
            if not stopped:
                logging.exception('Chat run failed: %s',job['id'])
            text = 'You stopped this reply. Finished images have been kept.' if stopped else plain(exc)
            e.db.update('runs',job['id'],status='cancelled' if stopped else 'failed',error=text,finished=time.time())
            e.trace(job,'error',{'detail':message(exc)})
            mark_images(e,job,text)
            e.publish(job,'run.error',{'message':text})
        finally:
            e.publish(job,'message.done',{'message_id':job['assistant_id']})
            e.events.publish('*','chats.changed',{'chat_id':job['chat_id']})
            notify(e)
