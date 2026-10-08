import gzip
import json
import sys
import time
from marionette_driver.by import By
from browser_session import browser
from browser_helpers import until
from studio_helpers import call, record, snapshot, console_errors, OUT
from studio_recovery_helpers import finished

name = sys.argv[1] if len(sys.argv)>1 else 'vision-prefix'
fixture = json.loads(gzip.decompress((OUT/(name+'-uat.json.gz')).read_bytes()))
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
    kv = run['settings']['kv_quantization']
    profile = next(p for p in answer['memory']['models'] if all(p[k]==run['settings'][k]
                   for k in ('model','quantization','precision','kv_quantization')))
    policy = 'mlp_fp32' if kv=='hqq_4' else 'mlp_down_fp32'
    assert profile['diagnostics']['prefix']['math_policy']==policy,profile
    assert profile['diagnostics']['prefix']['last_reused_tokens']>=64,profile
    assert not console_errors(d)
    snapshot(d,name+'-review')
    record(name+'-review',{'status':'PASS','chat':chat,'image':image,'run':run,
           'seconds':time.monotonic()-started,'actual_image_reused':True})
    print('Firefox actual-image follow-up with production prefix hit PASS',flush=True)
