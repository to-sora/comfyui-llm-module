import time
from marionette_driver.by import By
from browser_session import browser
from browser_helpers import until
from studio_helpers import call,record,snapshot,console_errors

with browser() as driver:
    driver.set_window_rect(width=1440,height=1000)
    driver.navigate('https://127.0.0.1:8189')
    until(lambda:driver.execute_script("return document.querySelectorAll('.chat-link').length>0"),30)
    driver.find_element(By.ID,'prompt').send_keys('Make two different pictures: a red ceramic mug on a white background, and a blue toy car on a white background. Check both pictures and tell me what you see.')
    driver.find_element(By.ID,'send').click()
    until(lambda:'/chats/' in driver.get_url(),30)
    chat=driver.get_url().rsplit('/',1)[-1]
    record('browser-chat',{'chat':chat,'started':time.time()})
    started,last=time.monotonic(),0
    streamed,preview=False,False
    while time.monotonic()-started<900:
        value=call('/chats/'+chat+'/messages')
        runs=list(value['runs'].values())
        run=runs[-1] if runs else None
        ui=driver.execute_script("return {text:document.getElementById('thread').innerText,preview:!!document.querySelector('.image-progress'),cards:document.querySelectorAll('.image-card').length}")
        preview=preview or ui['preview']
        if run and run['status']=='running' and any(m['role']=='assistant' and m['parts'] for m in value['messages']):
            streamed=streamed or len(ui['text'])>190
        if run and run['status'] not in ('queued','running'):
            break
        if time.monotonic()-last>30:
            print(run['status'] if run else 'waiting',ui,flush=True)
            snapshot(driver,'generation-progress')
            last=time.monotonic()
        time.sleep(1)
    snapshot(driver,'generation-finished')
    trace=call('/debug/runs/'+run['id']) if run else {}
    record('generation',{'state':value,'trace':trace,'streamed':streamed,'preview':preview,'console':console_errors(driver)})
    print({'chat':chat,'status':run['status'] if run else None,'error':run.get('error') if run else None,'streamed':streamed,'preview':preview},flush=True)
    assert run and run['status']=='done',trace
    images=[i for i in value['images'].values() if i['kind']=='generated' and i['file']]
    assert len(images)==2,images
    assert len({i['recipe']['seed'] for i in images})==2
    assert all(900000<=i['width']*i['height']<=1100000 and i['recipe']['cfg']==5.5 for i in images)
    assert not console_errors(driver)
