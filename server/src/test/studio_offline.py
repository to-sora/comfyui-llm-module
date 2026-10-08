import hashlib
import json
import ssl
import time
import urllib.request
from marionette_driver.by import By
from browser_session import browser
from browser_helpers import until
from studio_helpers import OUT,call,record,snapshot,console_errors
from studio_library_helpers import press
from studio_recovery_helpers import finished
from studio_core_restart import start,stop

started=time.monotonic()
chat=json.loads((OUT/'browser-chat.json').read_text())['chat']
with browser() as d:
    d.set_window_rect(width=1440,height=1000)
    d.navigate('https://127.0.0.1:8189/chats/'+chat)
    until(lambda:d.execute_script("return !!document.querySelector('.image-card:not(:disabled)')"),30)
    image=next(i for i in call('/chats/'+chat+'/messages')['images'].values() if i['file'])
    prior=set(call('/chats/'+chat+'/messages')['runs'])
    stop()
    try:
        boot=call('/bootstrap')
        assert boot['error']=='The image engine is unavailable. Reconnecting…',boot['error']
        with urllib.request.urlopen('https://127.0.0.1:8189/api/images/'+image['id'],context=ssl._create_unverified_context()) as response:
            assert 'immutable' in response.headers['Cache-Control']
            assert hashlib.sha256(response.read()).hexdigest()==image['sha256']
        d.find_element(By.CSS_SELECTOR,'.image-card:not(:disabled)').click()
        until(lambda:d.execute_script("return document.querySelector('.picture-plane img')?.naturalWidth>0"),30)
        snapshot(d,'engine-offline-viewer')
        d.find_element(By.CSS_SELECTOR,'[aria-label="Close image viewer"]').click()
        d.find_element(By.ID,'prompt').send_keys('What is 17 plus 25? Reply with only the number.')
        d.find_element(By.ID,'send').click()
        ident=until(lambda:next(iter(set(call('/chats/'+chat+'/messages')['runs'])-prior),None),30)
        run=until(lambda:finished(ident),30)
        assert run['status']=='failed' and run['error'],run
        snapshot(d,'engine-offline-error')
    finally:
        start()
    before=set(call('/chats/'+chat+'/messages')['runs'])
    press(d,'Try again')
    ident=until(lambda:next(iter(set(call('/chats/'+chat+'/messages')['runs'])-before),None),30)
    run=until(lambda:finished(ident),180)
    assert run['status']=='done',run.get('error')
    answer=[s['response']['content'] for s in run['trace']['steps'] if s['kind']=='assistant'][-1]
    assert answer.strip()=='42',answer
    assert not console_errors(d)
record('engine-offline',{'status':'PASS','local_original_sha256':image['sha256'],
    'plain_offline_error':True,'immutable_while_core_stopped':True,'retry_answer':answer,
    'services_left_running':True,'seconds':time.monotonic()-started})
print('Firefox actual engine outage, local original, plain error, reconnect and retry PASS')
