import json
import time
from marionette_driver.by import By
from browser_session import browser
from browser_helpers import until
from studio_helpers import OUT,call,record,snapshot,console_errors
from studio_recovery_helpers import finished,restart
from studio_library_helpers import press

started=time.monotonic()
restart()
chat=json.loads((OUT/'recovery.json').read_text())['chat']
prior=set(call('/chats/'+chat+'/messages')['runs'])
with browser() as d:
    d.set_window_rect(width=1440,height=1000)
    d.navigate('https://127.0.0.1:8189/chats/'+chat)
    until(lambda:d.execute_script("return !!document.querySelector('.run-error button')"),30)
    press(d,'Try again')
    def created():
        return next(iter(set(call('/chats/'+chat+'/messages')['runs'])-prior),None)
    ident=until(created,30)
    result=until(lambda:finished(ident),240)
    record('retry-run',result)
    assert result['status']=='done',result.get('error')
    page=call('/chats/'+chat+'/messages')
    images=[i for i in page['images'].values() if i['message_id']==result['assistant_id'] and i['file']]
    assert len(images)==4,len(images)
    until(lambda:d.execute_script("return document.querySelectorAll('.image-card:not(:disabled)').length>=4"),30)
    snapshot(d,'retry-finished')
    d.find_element(By.ID,'prompt').send_keys('Which four objects did I ask you to make? Answer briefly, without making more pictures.')
    before=set(page['runs'])
    d.find_element(By.ID,'send').click()
    follow=until(lambda:next(iter(set(call('/chats/'+chat+'/messages')['runs'])-before),None),30)
    final=until(lambda:finished(follow),90)
    assert final['status']=='done',final.get('error')
    steps=final['trace']['steps']
    answer=[s['response']['content'] for s in steps if s['kind']=='assistant'][-1]
    assert all(word in answer.lower() for word in ('mug','bowl','plate','bottle')),answer
    history=next(s['body']['messages'] for s in steps if s['kind']=='request')
    assert any('Earlier request status: interrupted' in str(m.get('content')) for m in history)
    assert not console_errors(d),console_errors(d)
    record('retry',{'status':'PASS','chat':chat,'images':len(images),'answer':answer,
        'interrupted_history_retained':True,'seconds':time.monotonic()-started})
    print('Firefox Try again, four actual images and interrupted-turn memory PASS')
