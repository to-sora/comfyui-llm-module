import json
import time
from marionette_driver.by import By
from marionette_driver.keys import Keys
from browser_session import browser
from browser_helpers import until
from studio_helpers import OUT,record,snapshot,console_errors
from studio_library_helpers import press

started=time.monotonic()
chat=json.loads((OUT/'browser-chat.json').read_text())['chat']
with browser() as d:
    d.set_window_rect(width=1440,height=1000)
    d.navigate('https://127.0.0.1:8189/chats/'+chat)
    until(lambda:d.execute_script("return !!document.querySelector('.image-card:not(:disabled)')"),30)
    d.find_element(By.CSS_SELECTOR,'.image-card:not(:disabled)').click()
    until(lambda:d.execute_script("return !document.querySelector('#viewer').hidden"),30)
    d.find_element(By.CSS_SELECTOR,'[aria-label="Expand image viewer"]').click()
    assert d.execute_script("return document.querySelector('#main').inert&&document.querySelector('#viewer').getAttribute('aria-modal')==='true'")
    d.find_element(By.CSS_SELECTOR,'#viewer button').send_keys(Keys.SHIFT,Keys.TAB,Keys.NULL)
    assert d.execute_script("return document.querySelector('#viewer').contains(document.activeElement)")
    d.find_element(By.CSS_SELECTOR,'#viewer button').send_keys(Keys.ESCAPE)
    assert d.execute_script("return document.querySelector('#viewer').hidden&&!document.body.classList.contains('viewer-full')&&!document.querySelector('#main').inert")
    d.set_window_rect(width=500,height=1166)
    with d.using_context(d.CONTEXT_CHROME):
        d.execute_script('gBrowser.selectedBrowser.fullZoom=1.28')
    d.find_element(By.ID,'menu').click()
    assert d.execute_script("return document.querySelector('#main').inert")
    d.find_element(By.ID,'close-sidebar').click()
    d.find_element(By.CSS_SELECTOR,'.image-card:not(:disabled)').click()
    until(lambda:d.execute_script("return document.querySelector('#viewer').getAttribute('aria-modal')==='true'"),30)
    picture=snapshot(d,'phone-viewer')
    press(d,'Use in chat')
    assert d.execute_script("return document.querySelector('#viewer').hidden&&document.activeElement.id==='prompt'&&document.querySelectorAll('.attachment').length===1")
    sizes=d.execute_script("return [...document.querySelectorAll('button,a.nav-link')].filter(n=>n.getClientRects().length&&!n.closest('[inert]')).map(n=>({label:n.getAttribute('aria-label')||n.textContent,width:n.getBoundingClientRect().width,height:n.getBoundingClientRect().height}))")
    assert all(n['width']>=44 and n['height']>=44 for n in sizes),sizes
    assert not picture['overflow'] and not console_errors(d)
record('accessibility',{'status':'PASS','modal_focus':True,'phone_use_in_chat':True,
    'visible_targets_44px':True,'phone_viewer':picture,'seconds':time.monotonic()-started})
print('Firefox fullscreen/mobile focus, Escape, touch targets and Use in chat PASS')
