import gzip
import json
import time
from pathlib import Path
import psutil
from marionette_driver.by import By
from server.src.test.browser_session import browser
from server.src.test.browser_helpers import until
from server.src.test.studio_helpers import call, record, snapshot, console_errors, OUT
from server.src.test.ram_observer import Observer, comfy
from server.src.test.r2_evidence import verify

prior=json.loads(gzip.decompress((OUT/'e2e-27b-261019.json.gz').read_bytes()))
chat=prior['chat']
service=json.loads(Path('plugin/data/service.json').read_text())
assert service['pid']==prior['comfy_pid']
result={'chat':chat,'service':service,'before':comfy('/llm/status'),'turns':[]}
observer=Observer(service['pid'])
try:
    with browser() as d:
        d.set_window_rect(width=1366,height=900)
        d.navigate('https://127.0.0.1:8189/chats/'+chat)
        until(lambda:d.execute_script("return document.querySelector('#attach')&&!document.querySelector('#attach').disabled"),30)
        for text in (
            'Without generating another image, recall the mug color I requested and the background mismatch you found. Answer in one sentence.',
            'Generate one studio photo of a single green ceramic mug on a plain white background. Then inspect the actual image and briefly report its color, object count and any mismatch.'
        ):
            known=set(call('/chats/'+chat+'/messages')['runs'])
            observer.phase='follow-up '+str(len(result['turns'])+1)
            d.find_element(By.ID,'prompt').send_keys(text)
            d.find_element(By.ID,'send').click()
            started=time.monotonic()
            run=None
            while time.monotonic()-started<600:
                page=call('/chats/'+chat+'/messages')
                run=next((v for k,v in page['runs'].items() if k not in known),None)
                if run and observer.low:
                    call('/runs/'+run['id']+'/cancel',{})
                    raise MemoryError('12 GiB planning threshold')
                if run and run['status'] not in ('queued','running'):break
                time.sleep(.5)
            else:
                if run:call('/runs/'+run['id']+'/cancel',{})
                raise TimeoutError('Follow-up deadline')
            result['turns'].append({'seconds':time.monotonic()-started,
                'run':call('/debug/runs/'+run['id']),'status':comfy('/llm/status')})
            print('FOLLOW-UP',run['status'],run.get('error'),flush=True)
            assert run['status']=='done',run.get('error')
            until(lambda:d.execute_script("return !document.querySelector('#attach').disabled"),30)
        result['viewport']=snapshot(d,'r2-multimessage-261019')
        result['console_errors']=console_errors(d)
finally:
    result['observation']=observer.close()
    result['after']=comfy('/llm/status')
    result['process_created_after']=psutil.Process(service['pid']).create_time()
    record('r2-multimessage-261019',result)
verify(prior,result)
