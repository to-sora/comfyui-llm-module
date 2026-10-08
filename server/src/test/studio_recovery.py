import time
from marionette_driver.by import By
from browser_session import browser
from browser_helpers import until
from studio_helpers import call,record,snapshot,console_errors
from studio_recovery_helpers import restart,drawing,finished,same_text
from studio_proxy import Proxy

started=time.monotonic()
chat=call('/chats',{})['id']
with Proxy() as proxy,browser() as d:
    d.set_window_rect(width=1440,height=1000)
    d.navigate(proxy.url+'/chats/'+chat)
    until(lambda:d.execute_script("return document.querySelectorAll('.suggestion').length===4"),30)
    d.find_element(By.ID,'prompt').send_keys('Write about 700 words of plain prose about light and color in product photography. Use no Markdown formatting or headings, and do not create an image.')
    d.find_element(By.ID,'send').click()
    until(lambda:d.execute_script("return !document.getElementById('stop').hidden&&!!document.querySelector('.assistant .message-content')"),90)
    run=next(iter(call('/chats/'+chat+'/messages')['runs']))
    d.navigate(d.get_url())
    until(lambda:d.execute_script("return !document.getElementById('stop').hidden"),30)
    proxy.invoke(proxy.outage(True))
    try:
        until(lambda:d.execute_script("return !document.getElementById('offline').hidden"),30)
        snapshot(d,'recovery-offline')
    finally:
        proxy.invoke(proxy.outage(False))
    result=until(lambda:finished(run),180)
    assert result['status']=='done',result.get('error')
    until(lambda:d.execute_script("return document.getElementById('stop').hidden&&document.getElementById('offline').hidden"),30)
    chars=same_text(d,chat)
    assert proxy.resumed, 'Browser did not reconnect with an SSE event cursor'
    d.find_element(By.ID,'prompt').send_keys('Make four different studio photographs of a red mug, blue bowl, yellow plate and green bottle, all on white backgrounds.')
    d.find_element(By.ID,'send').click()
    until(drawing,120)
    current=list(call('/chats/'+chat+'/messages')['runs'])[-1]
    restart()
    until(lambda:d.execute_script("return document.querySelector('.run-error')?.textContent.includes('restart')"),45)
    recovered=call('/debug/runs/'+current)
    assert recovered['status']=='interrupted',recovered['status']
    images=call('/chats/'+chat+'/messages')['images'].values()
    assert all(i['file'] or i['recipe'].get('error') for i in images)
    snapshot(d,'recovery-restart')
    record('recovery',{'status':'PASS','chat':chat,'stream_chars':chars,
        'refresh_and_reconnect_exact':True,'interrupted_cards_terminal':True,'run':current,
        'seconds':time.monotonic()-started})
    print('Refresh, offline SSE replay without duplicate text, restart and interrupted cards PASS')
