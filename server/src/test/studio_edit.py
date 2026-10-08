import time
import sys
import numpy as np
from PIL import Image
from pillow_heif import register_heif_opener
from marionette_driver.by import By
from browser_session import browser
from browser_helpers import until
from studio_helpers import ROOT,record,snapshot,console_errors
from studio_mask_helpers import press,paint,wait

register_heif_opener()
tag=sys.argv[1]+'-' if len(sys.argv)>1 else ''
big=ROOT/'server/data/tmp/studio-phone.png'
odd=ROOT/'server/data/tmp/studio-odd.heic'
Image.new('RGB',(8000,6000),'steelblue').save(big)
Image.new('RGB',(321,241),'steelblue').save(odd,format='HEIF')
try:
 started=time.monotonic()
 with browser() as d:
    d.set_window_rect(width=1440,height=1000)
    d.navigate('https://127.0.0.1:8189')
    until(lambda:d.execute_script("return document.querySelectorAll('.chat-link').length>0"),30)
    d.find_element(By.ID,'files').send_keys(str(big)+'\n'+str(odd))
    until(lambda:d.execute_script("return document.querySelectorAll('.attachment').length==2"),30)
    d.find_element(By.ID,'prompt').send_keys('Briefly describe these two attached pictures.')
    d.find_element(By.ID,'send').click()
    until(lambda:'/chats/' in d.get_url(),30)
    chat=d.get_url().rsplit('/',1)[-1]
    value,run=wait(d,chat)
    sources=list(value['images'].values())
    assert sorted((i['width'],i['height']) for i in sources)==[(321,241),(4096,3072)]
    source=next(i for i in sources if i['width']==321)
    d.find_element(By.CSS_SELECTOR,'[data-image="'+source['id']+'"]').click()
    until(lambda:d.execute_script("return !document.getElementById('viewer').hidden"),30)
    press(d,'Edit area');time.sleep(.4)
    controls=paint(d)
    d.find_element(By.CSS_SELECTOR,'.mask-tools textarea').send_keys('Add a small red star in this blue area.')
    snapshot(d,tag+'painted-area')
    press(d,'Send edit')
    value,edited=wait(d,chat,run['id'])
    output=next(i for i in value['images'].values() if i['kind']=='generated' and i['parents']==[source['id']])
    mask=value['images'][output['recipe']['mask']]
    def pixels(i):return np.array(Image.open(ROOT/'server/data/assets'/i['file']).convert('RGBA'))
    a,b=pixels(source),pixels(output)
    area=pixels(mask)[:,:,0]>0
    assert a.shape==b.shape==(241,321,4)
    assert np.array_equal(a[~area],b[~area])
    changed=int(np.any(a[area]!=b[area],axis=1).sum());assert changed>0
    assert not console_errors(d)
    record(tag+'edit-result',{'chat':chat,'source':source['id'],'output':output['id'],
        'seconds':time.monotonic()-started,
        'outside_unchanged':True,'changed_pixels':changed,'HEIC':True,'phone':[4096,3072],'controls':controls})
    snapshot(d,tag+'edit-finished')
    print('Browser upload / HEIC / painted edit passed',flush=True)
finally:
 big.unlink(missing_ok=True);odd.unlink(missing_ok=True)
