import time
from marionette_driver.by import By
from marionette_driver.keys import Keys
from browser_session import browser
from browser_helpers import until
from studio_helpers import call,record,snapshot,console_errors
from studio_library_helpers import press
from studio_recovery_helpers import finished

started=time.monotonic()
with browser() as d:
    d.set_window_rect(width=1440,height=1000)
    d.navigate('https://127.0.0.1:8189/')
    until(lambda:d.execute_script("return document.querySelectorAll('.suggestion').length===4"),30)
    d.find_element(By.CSS_SELECTOR,'.suggestion').click()
    prompt=d.find_element(By.ID,'prompt')
    assert prompt.get_property('value')
    prompt.clear()
    prompt.send_keys('Compare PNG and JPEG in a small Markdown table.')
    prompt.send_keys(Keys.SHIFT,Keys.ENTER,Keys.NULL)
    assert '\n' in prompt.get_property('value')
    prompt.send_keys('Then show a short Python code block that prints hello. Do not create an image.',Keys.ENTER)
    until(lambda:'/chats/' in d.get_url(),30)
    chat=d.get_url().rsplit('/',1)[1]
    rid=until(lambda:next(iter(call('/chats/'+chat+'/messages')['runs']),None),30)
    result=until(lambda:finished(rid),120)
    assert result['status']=='done',result.get('error')
    until(lambda:d.execute_script("return !!document.querySelector('.markdown table')&&!!document.querySelector('.code-block')"),30)
    code=d.find_element(By.CSS_SELECTOR,'.code-block code').text
    press(d,'Copy code')
    prompt.click();prompt.send_keys(Keys.CONTROL,'v',Keys.NULL)
    until(lambda:prompt.get_property('value')==code,10)
    prompt.clear()
    press(d,'Copy reply')
    prompt.click();prompt.send_keys(Keys.CONTROL,'v',Keys.NULL)
    until(lambda:'PNG' in prompt.get_property('value') and '```' in prompt.get_property('value'),10)
    prompt.clear()
    snapshot(d,'markdown-copy')
    d.find_element(By.ID,'chat-menu').click()
    field=d.find_element(By.CSS_SELECTOR,'#dialog input')
    field.clear();field.send_keys('UAT format comparison')
    press(d,'Save title')
    until(lambda:d.find_element(By.ID,'chat-title').text=='UAT format comparison',30)
    d.navigate(d.get_url())
    until(lambda:d.find_element(By.ID,'chat-title').text=='UAT format comparison',30)
    d.find_element(By.ID,'chat-menu').click();press(d,'Delete chat');press(d,'Delete')
    until(lambda:d.get_url().endswith('/'),30)
    assert chat not in {c['id'] for c in call('/chats')['chats']}
    assert not console_errors(d)
record('basics',{'status':'PASS','enter_shift_enter':True,'markdown_table_code':True,
    'copy_code_reply':True,'rename_refresh_delete':True,'seconds':time.monotonic()-started})
print('Firefox suggestions, Enter/Shift+Enter, Markdown/copy and chat management PASS')
