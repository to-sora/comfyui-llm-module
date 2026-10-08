import gzip
import json
import sys
import time
from marionette_driver.by import By
from browser_session import browser
from browser_helpers import until
from studio_helpers import OUT,call,record,snapshot,console_errors
from studio_delay import Delayed
from studio_mask_helpers import press,paint
from studio_mask_pixels import verify

ref=sys.argv[1] if len(sys.argv)>1 else None
name='mask-navigation-before-fix' if ref else 'mask-navigation'
if len(sys.argv)>2: name=sys.argv[2]
fixture=json.loads(gzip.decompress((OUT/'engine-recheck.json.gz').read_bytes()))
a,source=fixture['chat'],fixture['image']['id']
b=call('/chats',{})['id']
call('/chats/'+b,{'title':'UAT mask destination B'},'PATCH')
started=time.monotonic()
with Delayed({('POST','/api/uploads'):3},ref) as proxy,browser() as d:
    d.set_window_rect(width=1440,height=1000)
    d.navigate(proxy.url+'/chats/'+a)
    until(lambda:not d.find_element(By.ID,'send').get_property('disabled'),30)
    d.find_element(By.CSS_SELECTOR,f'[data-image="{source}"]').click()
    until(lambda:d.execute_script("return !document.getElementById('viewer').hidden"),30)
    press(d,'Edit area');paint(d)
    d.find_element(By.CSS_SELECTOR,'.mask-tools textarea').send_keys('Paint a small red star in this area.')
    press(d,'Send edit')
    until(lambda:'/api/uploads' in proxy.posts,30)
    d.find_element(By.CSS_SELECTOR,'[aria-label="Close image viewer"]').click()
    d.find_element(By.CSS_SELECTOR,f'a[href="/chats/{b}"]').click()
    until(lambda:d.find_element(By.ID,'chat-title').text=='UAT mask destination B',30)
    d.find_element(By.ID,'prompt').send_keys('Keep this draft in chat B')
    target=until(lambda:next((p.split('/')[3] for p in proxy.posts
                             if p.endswith('/messages')),None),30)
    def done():
        page=call('/chats/'+target+'/messages')
        return page if page['runs'] and all(r['status'] not in ('queued','running')
                                           for r in page['runs'].values()) else None
    page=until(done,300)
    result={'source':ref or 'working tree','expected_chat':a,'sent_chat':target,
            'url':d.get_url(),'draft':d.find_element(By.ID,'prompt').get_property('value'),
            'destination_messages':len(call('/chats/'+b+'/messages')['messages']),
            'console':console_errors(d),'seconds':time.monotonic()-started}
    record(name,result);snapshot(d,name)
    assert target==a and result['url'].endswith('/'+b),result
    assert result['destination_messages']==0 and result['draft']=='Keep this draft in chat B',result
    assert all(r['status']=='done' for r in page['runs'].values()),page
    result.update(verify(page,source));assert not result['console']
    record(name,{**result,'status':'PASS'})
    print('Painted edit stays in its original chat; other draft and unmasked pixels preserved PASS',flush=True)
