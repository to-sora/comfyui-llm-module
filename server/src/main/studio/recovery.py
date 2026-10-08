import logging
import time
from .run_error import mark_images


async def recover(e):
    for run in e.db.all("SELECT * FROM runs WHERE status IN ('running','queued')"):
        for prompt in run['trace'].get('prompt_ids', []):
            try:
                await e.comfy.cancel(prompt)
            except Exception:
                logging.exception('Could not cancel an interrupted prompt')
        text='This request was interrupted by a restart. Try again to continue.'
        e.db.update('runs',run['id'],status='interrupted',finished=time.time(),error=text,cancelled=0)
        mark_images(e,run,text)
        e.publish(run,'run.error',{'message':text})
        e.publish(run,'message.done',{'message_id':run['assistant_id']})
    e.events.publish('*','chats.changed',{})
