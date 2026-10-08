import sys
from marionette_driver.by import By
from browser_session import browser
from browser_helpers import until
from studio_helpers import ROOT,OUT,call,record,snapshot,console_errors
from studio_delay import Delayed

ref=sys.argv[1] if len(sys.argv)>1 else None
name='upload-race-before-fix' if ref else 'upload-race'
a,b=[call('/chats',{})['id'] for _ in range(2)]
call('/chats/'+b,{'title':'UAT upload destination B'},'PATCH')
path=ROOT/'server/data/tmp'/('upload-route-'+a+'.png')
path.write_bytes((OUT/'engine-recheck-image.png').read_bytes())
key=('POST','/api/uploads')
try:
    with Delayed({key:3},ref) as proxy,browser() as d:
        d.navigate(proxy.url+'/chats/'+a)
        until(lambda:not d.find_element(By.ID,'send').get_property('disabled'),30)
        d.find_element(By.ID,'prompt').send_keys('What is shown in this photo?')
        d.find_element(By.ID,'files').send_keys(str(path))
        until(lambda:'/api/uploads' in proxy.posts,30)
        disabled=d.find_element(By.ID,'send').get_property('disabled')
        d.find_element(By.ID,'send').click()
        d.find_element(By.CSS_SELECTOR,f'a[href="/chats/{b}"]').click()
        until(lambda:d.find_element(By.ID,'chat-title').text=='UAT upload destination B',30)
        until(lambda:key in proxy.done,30)
        uploaded=until(lambda:next((i for i in call('/images')['images']
                                   if i['recipe'].get('name')==path.name),None),30)
        message_posts=[p for p in proxy.posts if p.endswith('/messages')]
        for target in {p.split('/')[3] for p in message_posts}:
            until(lambda:all(r['status'] not in ('queued','running') for r in
                             call('/chats/'+target+'/messages')['runs'].values()),120)
        result={'source':ref or 'working tree','send_disabled_during_upload':disabled,
                'message_posts':message_posts,'image_in_library':uploaded['id'],
                'destination_chips':d.execute_script("return document.querySelectorAll('.attachment').length"),
                'console':console_errors(d)}
        record(name,result);snapshot(d,name)
        assert disabled and not message_posts and result['destination_chips']==0,result
        assert not result['console']
        record(name,{**result,'status':'PASS'})
        print('Upload blocks early send; switching chats keeps image in Library only PASS',flush=True)
finally:
    path.unlink(missing_ok=True)
