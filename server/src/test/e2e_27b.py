import time
from pathlib import Path
import json
from marionette_driver.by import By
from server.src.test.browser_session import browser
from server.src.test.browser_helpers import until
from server.src.test.studio_helpers import call,record,snapshot,console_errors
from server.src.test.ram_observer import Observer,comfy

profile='Qwen3.8-27B'
original=call('/bootstrap')['settings']
chat=call('/chats',{})['id']
call('/chats/'+chat,{'title':'27B end-to-end RAM observation'},'PATCH')
settings={**original,'chat_id':chat,'assistant':{**original['assistant'],'model':profile,
    'quantization':'bnb_nf4','precision':'bfloat16','kv_quantization':'hqq_8',
    'context_tokens':8192,'max_tokens':512}}
pid=json.loads(Path('plugin/data/service.json').read_text())['pid']
observer=Observer(pid)
result={'profile':profile,'chat':chat,'comfy_pid':pid,'settings':settings['assistant']}
try:
    call('/settings',settings,'PUT')
    with browser() as d:
        d.set_window_rect(width=1366,height=900)
        d.navigate('https://127.0.0.1:8189/chats/'+chat)
        until(lambda:d.execute_script("return document.querySelector('#attach')&&!document.querySelector('#attach').disabled"),30)
        text='Generate one realistic studio photograph of a single blue ceramic mug on a plain white tabletop and background. No text or extra objects. Then inspect the actual generated image and briefly report its visible color, object count and any mismatch.'
        d.find_element(By.ID,'prompt').send_keys(text)
        observer.phase='27B → SDXL → 27B'
        started=time.monotonic()
        d.find_element(By.ID,'send').click()
        run=None
        while time.monotonic()-started<900:
            page=call('/chats/'+chat+'/messages')
            run=next(iter(page['runs'].values()),None)
            if run and observer.low:
                call('/runs/'+run['id']+'/cancel',{})
                raise MemoryError('Stopped at the 12 GiB planning safety threshold')
            if run and run['status'] not in ('queued','running'):break
            time.sleep(.5)
        else:
            if run:call('/runs/'+run['id']+'/cancel',{})
            raise TimeoutError('27B workflow deadline')
        result.update(seconds=time.monotonic()-started,page=page,run=call('/debug/runs/'+run['id']),
            viewport=snapshot(d,'e2e-27b-261019'),console_errors=console_errors(d))
        print('RESULT',run['status'],run.get('error'),round(result['seconds'],2),flush=True)
        assert run['status']=='done',run.get('error')
        assert any(i['file'] for i in page['images'].values())
        assert len([s for s in result['run']['trace']['steps'] if s['kind']=='assistant'])>=2
        observer.phase='idle'
        time.sleep(2)
finally:
    result['observation']=observer.close()
    result['final_status']=comfy('/llm/status')
    record('e2e-27b-261019',result)
    call('/settings',original,'PUT')
    print('RECORDED',chat,flush=True)
