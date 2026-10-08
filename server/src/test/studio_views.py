import json
import time
from marionette_driver.by import By
from browser_session import browser
from browser_helpers import until
from studio_helpers import OUT,record,snapshot,console_errors,saved_settings


def button(d,text):
    d.find_element(By.XPATH,"//button[normalize-space(.)="+json.dumps(text)+"]").click()


started=time.monotonic()
with saved_settings(),browser() as d:
    chat=json.loads((OUT/'browser-chat.json').read_text())['chat']
    d.set_window_rect(width=1440,height=1000)
    d.navigate('https://127.0.0.1:8189/chats/'+chat)
    until(lambda:d.execute_script("return document.querySelectorAll('.image-card:not(:disabled)').length==2"),30)
    d.execute_script("document.getElementById('thread').scrollTop=0")
    d.find_element(By.CSS_SELECTOR,'.image-card').click()
    until(lambda:d.execute_script("return !document.getElementById('viewer').hidden"),30)
    time.sleep(.6)
    sizes=[snapshot(d,'chat-viewer')]
    button(d,'100%');button(d,'Fit')
    d.find_element(By.CSS_SELECTOR,'[aria-label="Expand image viewer"]').click()
    time.sleep(.4)
    sizes.append(snapshot(d,'viewer-full'))
    button(d,'Edit area')
    assert d.execute_script("return !!document.querySelector('canvas')")
    snapshot(d,'viewer-mask')
    d.find_element(By.CSS_SELECTOR,'[aria-label="Close image viewer"]').click()
    button(d,'Settings')
    d.execute_script("document.querySelector('[name=technical]').checked=true")
    button(d,'Save')
    button(d,'Debug')
    until(lambda:d.execute_script("return document.querySelectorAll('.trace-step').length>0"),30)
    snapshot(d,'debug-trace')
    assert not d.execute_script("return !!document.querySelector('#debug-panel input,#debug-panel select')")
    d.find_element(By.CSS_SELECTOR,'[aria-label="Close Debug"]').click()
    d.find_element(By.CSS_SELECTOR,'a[href="/library"]').click()
    until(lambda:d.execute_script("return document.querySelectorAll('.library-card').length>0"),30)
    sizes.append(snapshot(d,'library'))
    d.find_element(By.CSS_SELECTOR,'.library-card input').click()
    assert d.execute_script("return !document.getElementById('selection-bar').hidden")
    d.navigate('https://127.0.0.1:8189/chats/'+chat)
    until(lambda:d.execute_script("return document.querySelectorAll('.image-card').length==2"),30)
    for name,w,h,zoom in [('portrait',500,1166,1.28),('large',1920,1400,1),('enlarged',1440,1100,2)]:
        d.set_window_rect(width=w,height=h)
        with d.using_context(d.CONTEXT_CHROME):
            d.execute_script('gBrowser.selectedBrowser.fullZoom=arguments[0]',script_args=[zoom])
        time.sleep(.5)
        sizes.append(snapshot(d,name))
    errors=console_errors(d)
    record('views',{'layouts':sizes,'console':errors,'seconds':time.monotonic()-started})
    print({'layouts':sizes,'errors':errors},flush=True)
    assert not any(s['overflow'] for s in sizes)
    assert not errors
