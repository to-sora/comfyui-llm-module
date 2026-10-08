import asyncio
import sys
import time
from marionette_driver.by import By
from browser_session import browser
from browser_helpers import until
from studio_helpers import call,record,snapshot,console_errors
from studio_proxy import Proxy


class SlowSend(Proxy):
    def __init__(self):
        super().__init__()
        self.creates = 0
        self.targets = []
        self.posting = 0

    async def forward(self, request):
        post = request.method=='POST'
        self.posting += int(post)
        try:
            if post and request.path=='/api/chats':
                self.creates += 1
                await asyncio.sleep(2)
            if post and request.path.endswith('/messages'):
                self.targets.append(request.path.split('/')[3])
            return await super().forward(request)
        finally:
            self.posting -= int(post)


name = sys.argv[1] if len(sys.argv)>1 else 'send-race'
started = time.monotonic()
with SlowSend() as proxy,browser() as d:
    d.navigate(proxy.url+'/')
    until(lambda:not d.find_element(By.ID,'send').get_property('disabled'),30)
    d.find_element(By.ID,'prompt').send_keys('What is 12 + 30? Reply only with the number.')
    d.find_element(By.ID,'send').click()
    d.find_element(By.ID,'send').click()
    until(lambda:proxy.targets and proxy.posting==0,30)
    chats = {ident:call('/chats/'+ident+'/messages') for ident in set(proxy.targets)}
    for ident in chats:
        until(lambda:all(r['status'] not in ('queued','running') for r in
                         call('/chats/'+ident+'/messages')['runs'].values()),120)
    result = {'chat_creations':proxy.creates,'message_posts':len(proxy.targets),
              'target_chats':proxy.targets,'url':d.get_url(),'seconds':time.monotonic()-started,
              'console':console_errors(d)}
    record(name,result);snapshot(d,name)
    assert proxy.creates==1 and len(proxy.targets)==1,result
    page = call('/chats/'+proxy.targets[0]+'/messages')
    assert len([m for m in page['messages'] if m['role']=='user'])==1
    assert '42' in ' '.join(p.get('text','') for m in page['messages']
                           if m['role']=='assistant' for p in m['parts'])
    assert not result['console']
    record(name,{**result,'status':'PASS','reply':'42'})
    print('Firefox double click makes one chat and one real reply PASS',flush=True)
