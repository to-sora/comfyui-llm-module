import sys
import time
from marionette_driver.by import By
from browser_session import browser
from browser_helpers import until
from studio_helpers import call,record,snapshot,console_errors
from studio_delay import Delayed

ref=sys.argv[1] if len(sys.argv)>1 else None
name='route-race-before-fix' if ref else 'route-race'
chats=[]
for title in ('UAT slow chat A','UAT latest chat B'):
    chat=call('/chats',{})['id']
    call('/chats/'+chat,{'title':title},'PATCH')
    chats.append(chat)
a,b=chats
key=('GET','/api/chats/'+a)
with Delayed({key:2},ref) as proxy,browser() as d:
    d.navigate(proxy.url+'/chats/'+b)
    until(lambda:not d.find_element(By.ID,'send').get_property('disabled'),30)
    d.find_element(By.CSS_SELECTOR,f'a[href="/chats/{a}"]').click()
    d.find_element(By.CSS_SELECTOR,f'a[href="/chats/{b}"]').click()
    until(lambda:key in proxy.done,30)
    time.sleep(.5)
    result={'source':ref or 'working tree','url':d.get_url(),
            'heading':d.find_element(By.ID,'chat-title').text,'expected_chat':b,
            'console':console_errors(d)}
    record(name,result);snapshot(d,name)
    assert result['url'].endswith('/'+b) and result['heading']=='UAT latest chat B',result
    assert not result['console']
    record(name,{**result,'status':'PASS'})
    print('Firefox late chat response cannot replace latest selection PASS',flush=True)
