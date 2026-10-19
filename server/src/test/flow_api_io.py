"""Real gateway/native jobs with scoped cancellation and RAM observation."""
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from plugin.src.test.api_client import request


def cancel(prompt):
    request('/api/jobs/'+prompt+'/cancel',{},binary=True)


def chat(body,observer):
    prompt=str(uuid.uuid4())
    with ThreadPoolExecutor(max_workers=1) as pool:
        future=pool.submit(request,'/v1/chat/completions',{**body,'comfy_prompt_id':prompt})
        deadline=time.monotonic()+360
        while not future.done():
            if observer.low or time.monotonic()>deadline:
                cancel(prompt)
                raise RuntimeError('LLM stopped: RAM guard or six-minute request limit')
            time.sleep(.5)
        return future.result()


def image(graph,observer):
    prompt=request('/prompt',{'prompt':graph})['prompt_id']
    complete=False
    try:
        deadline=time.monotonic()+300
        while time.monotonic()<deadline and not observer.low:
            result=request('/history/'+prompt).get(prompt)
            if result:
                complete=True
                if result['status']['status_str']!='success':
                    raise RuntimeError(str(result['status']))
                return {'prompt_id':prompt,'outputs':result['outputs']}
            time.sleep(.5)
        raise RuntimeError('Image stopped: RAM guard or five-minute request limit')
    finally:
        if not complete:cancel(prompt)
        request('/history',{'delete':[prompt]},binary=True)
