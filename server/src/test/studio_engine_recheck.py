import ssl
import sys
import time
import urllib.request
from marionette_driver.by import By
from browser_session import browser
from browser_helpers import until
from studio_helpers import call, record, snapshot, console_errors, OUT, saved_settings
from studio_recovery_helpers import finished

name = sys.argv[1] if len(sys.argv)>1 else 'engine-recheck'
started = time.monotonic()
with saved_settings(), browser() as d:
    if len(sys.argv)>2:
        settings = call('/bootstrap')['settings']
        settings['assistant']['kv_quantization'] = sys.argv[2]
        call('/settings',settings,'PUT')
    d.set_window_rect(width=1440,height=1000)
    d.navigate('https://127.0.0.1:8189/')
    until(lambda:d.execute_script("return !!document.getElementById('prompt')&&!document.getElementById('send').disabled"),30)
    d.find_element(By.ID,'prompt').send_keys('Make a studio photograph of one blue ceramic cup on a plain white background. Check the finished picture and describe what you actually see.')
    d.find_element(By.ID,'send').click()
    until(lambda:'/chats/' in d.get_url(),30)
    chat = d.get_url().rsplit('/',1)[1]
    if len(sys.argv)>2:
        call('/settings',{**settings,'chat_id':chat},'PUT')
    ident = until(lambda:next(iter(call('/chats/'+chat+'/messages')['runs']),None),30)
    run = until(lambda:finished(ident),600)
    assert run['status']=='done',run
    page = call('/chats/'+chat+'/messages')
    images = [i for i in page['images'].values() if i['kind']=='generated' and i['file']]
    assert len(images)==1,images
    image = images[0]
    requests = [s['body'] for s in run['trace']['steps'] if s['kind']=='request']
    assert len(requests)>=2 and any(isinstance(m.get('content'),list) and
        any(p['type']=='image_url' for p in m['content']) for m in requests[-1]['messages'])
    until(lambda:d.execute_script("return !!document.querySelector('.image-card img')"),30)
    d.find_element(By.CSS_SELECTOR,'.image-card').click()
    until(lambda:d.execute_script("const i=document.querySelector('#viewer .picture-plane img');return i?.complete&&i.naturalWidth>0"),30)
    snapshot(d,name)
    assert not console_errors(d)
    with urllib.request.urlopen('https://127.0.0.1:8189/api/images/'+image['id'],
            context=ssl._create_unverified_context()) as response:
        (OUT/(name+'-image.png')).write_bytes(response.read())
    record(name,{'status':'PASS','chat':chat,'run':run,'image':image,
        'seconds':time.monotonic()-started,'actual_pixels_reviewed':True})
    print('Firefox LLM → SDXL → actual-image review PASS',chat,flush=True)
