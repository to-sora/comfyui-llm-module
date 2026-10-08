import uuid
import time
from .workflows import build
from .image_inputs import prepare
from .image_events import callback
from .image_finish import finish
from .store import encode
from ..prompt_cleanup import cleanup


async def start(e,run,tasks):
    e.check(run)
    prompt=str(uuid.uuid4())
    p=dict(tasks[0]['params'],output_key=tasks[0]['id'])
    source,mask,original,paint=await prepare(e,run,tasks[0],prompt)
    p.update({k:tasks[0]['params'][k] for k in ('width','height')})
    graph=build(p,[t['params']['seed'] for t in tasks],source,mask)
    future=await e.comfy.events.subscribe(prompt,callback(e,run,tasks))
    e.prompts[run['id']].add(prompt)
    trace=e.db.get('runs',run['id'])['trace']
    trace.setdefault('prompt_ids',[]).append(prompt)
    e.db.update('runs',run['id'],trace_json=encode(trace))
    try:
        e.check(run)
        await e.comfy.request('/prompt',{'prompt':graph,'prompt_id':prompt,'client_id':e.comfy.events.client_id})
        e.check(run)
    except BaseException:
        await cleanup(e.comfy,prompt,False,future)
        e.prompts[run['id']].discard(prompt)
        raise
    return (prompt,future,tasks,original,paint,time.monotonic())


async def wait(e,run,value):
    prompt,future,tasks,original,mask,started=value
    completed=False
    try:
        result=await e.comfy.history(prompt,future)
        completed=True
        await finish(e,run,tasks,prompt,result['outputs'],original,mask)
        e.trace(run,'images',{'prompt_id':prompt,'images':[t['id'] for t in tasks],
            'seconds':time.monotonic()-started,'checkpoint':tasks[0]['params']['checkpoint']})
    finally:
        await cleanup(e.comfy,prompt,completed,future)
        e.prompts[run['id']].discard(prompt)
