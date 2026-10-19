"""After e2e_27b, select cuda:0 explicitly through the native node API."""
import gzip
import json
import time
from pathlib import Path
from plugin.src.main.gateway_graph import graph
from plugin.src.test.api_client import request
from server.src.test.studio_helpers import OUT,record
from server.src.test.ram_observer import Observer,comfy

first=json.loads(gzip.decompress((OUT/'e2e-27b-261019.json.gz').read_bytes()))
service=json.loads(Path('plugin/data/service.json').read_text())
assert service['pid']==first['comfy_pid']
before=comfy('/llm/status')
models=lambda s:[m for m in s['models'] if m['model']=='Qwen3.8-27B']
assert len(models(before))==1 and models(before)[0]['device']=='cuda:0'
body={'model':'Qwen3.8-27B','quantization':'bnb_nf4','precision':'bfloat16',
    'kv_quantization':'hqq_8','context_tokens':8192,'max_tokens':32,'temperature':0,
    'messages':[{'role':'user','content':'What is 6 times 7? Reply with only the number.'}]}
workflow=graph(body)
workflow['1']['inputs']['device']='cuda:0'
observer=Observer(service['pid'])
observer.phase='explicit cuda:0 after auto'
result={'service':service,'before':before,'workflow':workflow}
ident=None
try:
    ident=request('/prompt',{'prompt':workflow})['prompt_id']
    start=time.monotonic()
    while time.monotonic()-start<120:
        if observer.low:raise MemoryError('12 GiB planning threshold')
        history=comfy('/history/'+ident)
        if ident in history:
            job=history[ident]
            assert job['status']['status_str']=='success',job['status']
            reply=json.loads(job['outputs']['2']['text'][0])
            assert reply['choices'][0]['message']['content'].strip()=='42',reply
            result.update(reply=reply,seconds=time.monotonic()-start)
            break
        time.sleep(.5)
    else:raise TimeoutError('Explicit-device request')
    after=result['after']=comfy('/llm/status')
    assert len(after['models'])==len(before['models']) and len(models(after))==1
    assert before['weight_reads']==after['weight_reads']
    assert before['ram_budget']['reservations']==after['ram_budget']['reservations']
    assert models(after)[0]['loads']==1
    assert models(after)[0]['transfers']==models(before)[0]['transfers']
    result['status']='PASS'
finally:
    if ident:
        if result.get('status')!='PASS':request('/interrupt',{'prompt_id':ident},binary=True)
        request('/history',{'delete':[ident]},binary=True)
    result['observation']=observer.close()
    record('device-alias-live-261019',result)
print('Live auto → cuda:0: one owner, one load, unchanged quota, answer 42')
