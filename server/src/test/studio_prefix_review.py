import gzip
import json
import time
from marionette_driver.by import By
from browser_session import browser
from browser_helpers import until
from studio_helpers import call, record, snapshot, console_errors, OUT
from studio_recovery_helpers import finished

fixture = json.loads(gzip.decompress((OUT/'vision-prefix-uat.json.gz').read_bytes()))
chat, image = fixture['chat'], fixture['image']['id']
started = time.monotonic()
old = set(call('/chats/'+chat+'/messages')['runs'])
with browser() as d:
    d.set_window_rect(width=1440,height=1000)
    d.navigate('https://127.0.0.1:8189/chats/'+chat)
    until(lambda:d.execute_script("return !!document.querySelector('.image-card')&&!document.getElementById('send').disabled"),30)
    d.find_element(By.CSS_SELECTOR,'.image-card').click()
    button = until(lambda:next((b for b in d.find_elements(By.CSS_SELECTOR,'#viewer button')
                               if b.text=='Use in chat'),None),30)
    button.click()
    until(lambda:d.execute_script("return document.querySelectorAll('#attachments .attachment').length>0"),10)
    d.find_element(By.ID,'prompt').send_keys('Describe the main object, its color, and the background in this picture. Do not edit it.')
    d.find_element(By.ID,'send').click()
    ident = until(lambda:next(iter(set(call('/chats/'+chat+'/messages')['runs'])-old),None),30)
    run = until(lambda:finished(ident),600)
    assert run['status']=='done',run
    steps = run['trace']['steps']
    answer = [s for s in steps if s['kind']=='assistant'][-1]
    content = answer['response'].get('content','').lower()
    assert any(w in content for w in ('cup','mug')) and 'blue' in content,answer
    assert not answer['response'].get('tool_calls'),answer
    profile = next(p for p in answer['memory']['models'] if p['model']==run['settings']['model']
                   and p['kv_quantization']=='hqq_8')
    assert profile['diagnostics']['prefix']['math_policy']=='mlp_down_fp32',profile
    assert profile['diagnostics']['prefix']['last_reused_tokens']>=64,profile
    assert not console_errors(d)
    snapshot(d,'vision-prefix-review')
    record('vision-prefix-review',{'status':'PASS','chat':chat,'image':image,'run':run,
           'seconds':time.monotonic()-started,'actual_image_reused':True})
    print('Firefox actual-image follow-up with production prefix hit PASS',flush=True)
