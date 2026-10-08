import asyncio
import sys
from marionette_driver.by import By
from browser_session import browser
from browser_helpers import until
from studio_helpers import call,record,snapshot,console_errors
from studio_proxy import Proxy
from studio_recovery_helpers import finished


class SlowStart(Proxy):
    async def forward(self, request):
        if request.path == '/api/bootstrap':
            await asyncio.sleep(4)
        return await super().forward(request)


name = sys.argv[1] if len(sys.argv)>1 else 'startup'
text = 'What is 17 + 25? Reply only with the number.'
with SlowStart() as proxy,browser() as d:
    d.set_window_rect(width=1440,height=1000)
    d.navigate(proxy.url+'/')
    until(lambda:d.execute_script("return !!document.getElementById('prompt')"),30)
    d.find_element(By.ID,'prompt').send_keys(text)
    initially_disabled = d.find_element(By.ID,'send').get_property('disabled')
    d.find_element(By.ID,'send').click()
    until(lambda:d.execute_script("return document.querySelectorAll('.suggestion').length===4"),30)
    preserved = d.find_element(By.ID,'prompt').get_property('value') == text
    result = {'initially_disabled':initially_disabled,'prompt_preserved':preserved,
              'bootstrap_delay_seconds':4,'real_https_relay':True}
    record(name,result)
    snapshot(d,name)
    assert preserved and initially_disabled,result
    until(lambda:not d.find_element(By.ID,'send').get_property('disabled'),30)
    d.find_element(By.ID,'send').click()
    until(lambda:'/chats/' in d.get_url(),30)
    chat = d.get_url().rsplit('/',1)[1]
    ident = until(lambda:next(iter(call('/chats/'+chat+'/messages')['runs']),None),30)
    run = until(lambda:finished(ident),120)
    assert run['status']=='done',run
    until(lambda:d.execute_script("return [...document.querySelectorAll('.assistant')].some(n=>n.innerText.includes('42'))"),30)
    assert not console_errors(d)
    result['header_title'] = d.find_element(By.ID,'chat-title').text
    result['stored_title'] = call('/chats/'+chat)['title']
    record(name,result)
    snapshot(d,name+'-reply')
    assert result['header_title']==result['stored_title'],result
    result.update(status='PASS',chat=chat,answer='42')
    record(name,result)
    print('Delayed startup preserves typed prompt; actual reply 42 PASS',flush=True)
