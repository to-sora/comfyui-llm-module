import json
import time
from marionette_driver.by import By
from browser_session import browser
from browser_helpers import until
from studio_helpers import OUT,call,record,snapshot,console_errors
from studio_transfer import insert

started=time.monotonic()
source=json.loads((OUT/'profiles.json').read_text())[0]['image']
created=[]
with browser() as d:
    d.set_window_rect(width=1440,height=1000)
    d.navigate('https://127.0.0.1:8189/')
    until(lambda:d.execute_script("return document.querySelectorAll('.suggestion').length===4"),30)
    for number,kind in enumerate(('paste','drop'),1):
        insert(d,source,kind)
        until(lambda:d.execute_script('return document.querySelectorAll(".attachment").length===arguments[0]',script_args=[number]),30)
    created=d.execute_script("return [...document.querySelectorAll('.attachment img')].map(n=>n.src.split('/').at(-2))")
    assert len(created)==2 and len(set(created))==2
    original=call('/images/'+source+'/info')
    assert all(call('/images/'+ident+'/info')['width']==original['width'] for ident in created)
    snapshot(d,'paste-drop')
    d.find_element(By.CSS_SELECTOR,'.attachment button').click()
    assert d.execute_script("return document.querySelectorAll('.attachment').length===1")
    assert not console_errors(d)
call('/images/actions',{'action':'delete','images':created})
record('attachment-events',{'status':'PASS','paste_and_drop_events':True,'actual_png_uploads':2,
    'native_image_paste':'Headless Firefox clipboard was empty; human check required','remove_chip':True,'seconds':time.monotonic()-started})
print('Firefox paste/drop events upload actual PNGs, attach two chips, remove and clean up PASS')
