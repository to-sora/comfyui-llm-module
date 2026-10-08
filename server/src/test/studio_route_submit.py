import sys
from marionette_driver.by import By
from browser_session import browser
from browser_helpers import until
from studio_helpers import call,record,snapshot,console_errors
from studio_delay import Delayed

ref=sys.argv[1] if len(sys.argv)>1 else None
name='route-submit-before-fix' if ref else 'route-submit'
a,b=[call('/chats',{})['id'] for _ in range(2)]
key=('GET','/api/chats/'+a)
with Delayed({key:3},ref) as proxy,browser() as d:
    d.navigate(proxy.url+'/chats/'+b)
    until(lambda:not d.find_element(By.ID,'send').get_property('disabled'),30)
    d.find_element(By.CSS_SELECTOR,f'a[href="/chats/{a}"]').click()
    d.find_element(By.ID,'prompt').send_keys('What is 19 + 23? Reply only with the number.')
    disabled=d.find_element(By.ID,'send').get_property('disabled')
    d.find_element(By.ID,'send').click()
    until(lambda:key in proxy.done,30)
    early=[p for p in proxy.posts if p.endswith('/messages')]
    if not early:
        until(lambda:not d.find_element(By.ID,'send').get_property('disabled'),30)
        d.find_element(By.ID,'send').click()
    target=until(lambda:next((p.split('/')[3] for p in proxy.posts
                             if p.endswith('/messages')),None),30)
    def done():
        page=call('/chats/'+target+'/messages')
        return page if page['runs'] and all(r['status'] not in ('queued','running')
                                           for r in page['runs'].values()) else None
    page=until(done,120)
    result={'source':ref or 'working tree','send_disabled_while_opening':disabled,
            'early_posts':early,'expected_chat':a,'sent_chat':target,
            'other_chat_messages':len(call('/chats/'+b+'/messages')['messages']),
            'console':console_errors(d)}
    record(name,result);snapshot(d,name)
    assert disabled and not early and target==a and result['other_chat_messages']==0,result
    assert all(r['status']=='done' for r in page['runs'].values()),page
    assert '42' in ' '.join(p.get('text','') for m in page['messages']
                           if m['role']=='assistant' for p in m['parts'])
    assert not result['console']
    record(name,{**result,'status':'PASS','reply':'42'})
    print('Send waits for the selected chat and delivers its preserved prompt PASS',flush=True)
