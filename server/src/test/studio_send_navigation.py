import sys
from marionette_driver.by import By
from browser_session import browser
from browser_helpers import until
from studio_helpers import call,record,snapshot,console_errors
from studio_delay import Delayed

ref=sys.argv[1] if len(sys.argv)>1 else None
name='send-navigation-before-fix' if ref else 'send-navigation'
b=call('/chats',{})['id']
call('/chats/'+b,{'title':'UAT destination B'},'PATCH')
with Delayed({('POST','/api/chats'):2},ref) as proxy,browser() as d:
    d.navigate(proxy.url+'/')
    until(lambda:not d.find_element(By.ID,'send').get_property('disabled'),30)
    d.find_element(By.ID,'prompt').send_keys('What is 15 + 27? Reply only with the number.')
    d.find_element(By.ID,'send').click()
    d.find_element(By.CSS_SELECTOR,f'a[href="/chats/{b}"]').click()
    until(lambda:d.find_element(By.ID,'chat-title').text=='UAT destination B',30)
    prompt=d.find_element(By.ID,'prompt');prompt.clear();prompt.send_keys('A draft for chat B')
    target=until(lambda:next((p.split('/')[3] for p in proxy.posts if p.endswith('/messages')),None),30)
    def done():
        page=call('/chats/'+target+'/messages')
        return page if page['runs'] and all(r['status']=='done' for r in page['runs'].values()) else None
    page=until(done,120)
    result={'source':ref or 'working tree','url':d.get_url(),'expected_chat':b,'sent_chat':target,
            'draft':d.find_element(By.ID,'prompt').get_property('value'),
            'destination_messages':len(call('/chats/'+b+'/messages')['messages']),
            'console':console_errors(d)}
    record(name,result);snapshot(d,name)
    assert target!=b and result['url'].endswith('/'+b),result
    assert result['draft']=='A draft for chat B' and result['destination_messages']==0,result
    assert '42' in ' '.join(p.get('text','') for m in page['messages']
                           if m['role']=='assistant' for p in m['parts'])
    assert not result['console']
    record(name,{**result,'status':'PASS','reply':'42'})
    print('Pending send stays in its original chat and preserves current draft PASS',flush=True)
