import asyncio
import logging
from collections import defaultdict
from . import image_job,cpu_job
from .image_store import metadata
from .store import encode
from ..errors import message, UserError
from ..prompt_cleanup import cleanup


def group(tasks):
    groups=defaultdict(list)
    for task in tasks:
        p=task['params']
        key=task['id'] if p.get('source') else encode({k:v for k,v in p.items() if k!='seed'})
        groups[key].append(task)
    result=[]
    for value in groups.values():
        result.append(value)
    return sorted(result,key=lambda values:values[0]['params']['checkpoint'])


def fail(e,run,tasks,exc):
    if not isinstance(exc,(UserError,asyncio.CancelledError)) and not e.db.get('runs',run['id'])['cancelled']:
        logging.error("Image batch failed",exc_info=(type(exc),exc,exc.__traceback__))
    for task in tasks:
        recipe={**task['params'],'error':message(exc)}
        e.db.update('images',task['id'],recipe_json=encode(recipe))
        e.publish(run,'image.error',{'image_id':task['id'],'message':'This image could not be finished'})


async def execute(e,run,tasks):
    remaining=list(tasks)
    while remaining:
        e.check(run)
        ready=[]
        for task in remaining:
            source=task['params'].get('source')
            if not source or metadata(e.db,source,run['chat_id'])['file']:
                ready.append(task)
        if not ready:
            for task in remaining:
                fail(e,run,[task],UserError('The source image was not completed'))
            break
        for task in ready:
            remaining.remove(task)
        gpu=[t for t in ready if t['params'].get('operation') not in ('upscale_image','remove_background')]
        submitted=[]
        try:
            for batch in group(gpu):
                try:
                    submitted.append(await image_job.start(e,run,batch))
                except Exception as exc:
                    e.check(run)
                    fail(e,run,batch,exc)
            waits=[asyncio.create_task(image_job.wait(e,run,value)) for value in submitted]
            cpu=[t for t in ready if t not in gpu]
            outcomes=await asyncio.gather(*waits,*(cpu_job.execute(e,run,t) for t in cpu),return_exceptions=True)
            for items,outcome in zip([v[2] for v in submitted]+[[t] for t in cpu],outcomes):
                if isinstance(outcome,BaseException):
                    fail(e,run,items,outcome)
            e.check(run)
        finally:
            for prompt,future,*_ in submitted:
                if not future.done():
                    await cleanup(e.comfy,prompt,False,future)
                e.prompts[run['id']].discard(prompt)
