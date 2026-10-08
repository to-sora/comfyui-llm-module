import uuid
import time
from .stream_parse import packets, merge
from .message_parts import delta
from .store import encode
from ..prompt_cleanup import cleanup


async def complete(e, run, messages, tools, visible=True, **options):
    e.check(run)
    prompt = str(uuid.uuid4())
    e.prompts[run['id']].add(prompt)
    trace = e.db.get('runs',run['id'])['trace']
    trace.setdefault('prompt_ids',[]).append(prompt)
    e.db.update('runs',run['id'],trace_json=encode(trace))
    body = {**run['settings'], 'messages':messages,'tools':tools,'stream':True,
            'stream_options':{'include_usage':True},'temperature':0,'enable_thinking':False,
            'parallel_tool_calls':True,'comfy_prompt_id':prompt, **options}
    body.pop('image_checkpoint',None)
    started, completed, usage = time.monotonic(), False, {}
    finished = False
    message = {'role':'assistant','content':None}
    e.trace(run,'request',{'body':body})
    try:
        async with e.comfy.client.post(e.comfy.url+'/v1/chat/completions',json=body) as response:
            if response.status >= 400:
                raise RuntimeError(f'Assistant request failed: {await response.text()}')
            async for value in packets(response):
                e.check(run)
                if value.get('error'):
                    raise RuntimeError(value['error'].get('message') or 'Assistant request failed')
                if value.get('usage'):
                    usage = value['usage']
                for choice in value.get('choices',[]):
                    finished = finished or bool(choice.get('finish_reason'))
                    part = choice.get('delta', {})
                    merge(message,part)
                    if visible and part.get('content'):
                        delta(e,run,part['content'])
        e.check(run)
        if not finished:
            raise ConnectionError('The assistant stream ended before the reply finished')
        completed = True
        e.trace(run,'assistant',{'seconds':time.monotonic()-started,'usage':usage,'response':message,
            'model':run['settings']['model'],'memory':await e.comfy.request('/llm/status')})
        return message
    finally:
        await cleanup(e.comfy,prompt,completed)
        e.prompts[run['id']].discard(prompt)
