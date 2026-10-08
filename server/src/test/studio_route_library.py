import sys
import time
from marionette_driver.by import By
from browser_session import browser
from browser_helpers import until
from studio_helpers import call,record,snapshot,console_errors
from studio_delay import Delayed

ref=sys.argv[1] if len(sys.argv)>1 else None
name='route-library-before-fix' if ref else 'route-library'
a,b=[call('/chats',{})['id'] for _ in range(2)]
call('/chats/'+a,{'title':'UAT old chat must not replace Library'},'PATCH')
key=('GET','/api/chats/'+a)
with Delayed({key:3},ref) as proxy,browser() as d:
    d.navigate(proxy.url+'/chats/'+b)
    until(lambda:not d.find_element(By.ID,'send').get_property('disabled'),30)
    d.find_element(By.CSS_SELECTOR,f'a[href="/chats/{a}"]').click()
    d.find_element(By.CSS_SELECTOR,'a[href="/library"]').click()
    until(lambda:key in proxy.done,30)
    time.sleep(.5)
    result={'source':ref or 'working tree','url':d.get_url(),
            'heading':d.find_element(By.ID,'chat-title').text,
            'library_visible':d.find_element(By.ID,'library').is_displayed(),
            'console':console_errors(d)}
    record(name,result);snapshot(d,name)
    assert result['url'].endswith('/library') and result['heading']=='Library',result
    assert result['library_visible'] and not result['console']
    record(name,{**result,'status':'PASS'})
    print('Library selection survives a late chat response PASS',flush=True)
