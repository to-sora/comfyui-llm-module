import time
from marionette_driver.by import By
from .browser_session import browser
from .browser_helpers import until
from .studio_helpers import call,record,snapshot,console_errors


original=call('/bootstrap')['settings']
chat=call('/chats',{})['id']
results=[]
try:
    with browser() as d:
        d.navigate('https://127.0.0.1:8189/chats/'+chat)
        until(lambda:d.execute_script("return document.querySelectorAll('.suggestion').length===4"),30)
        for width,height in [(1366,900),(430,932),(1920,1200)]:
            d.set_window_rect(width=width,height=height)
            if width<700:d.find_element(By.ID,'menu').click()
            d.find_element(By.ID,'settings').click()
            until(lambda:d.execute_script("return document.querySelector('#dialog form')"),10)
            d.execute_script('''const f=document.querySelector('#dialog form');
                f.querySelector('details').open=true;
                f.elements.context_tokens.value=35000;
                f.elements.max_tokens.value=12000;
                f.elements.max_image_tokens.value=16000;
                f.elements.enable_thinking.checked=true;
                f.elements.parallel_tool_calls.checked=false;''')
            results.append(snapshot(d,'flow-settings-'+str(width)))
            d.execute_script("document.querySelector('[name=enable_thinking]').scrollIntoView({block:'start'})")
            results.append(snapshot(d,'flow-settings-limits-'+str(width)))
            d.find_element(By.CSS_SELECTOR,'#dialog button[type=submit]').click()
            until(lambda:d.execute_script("return !document.querySelector('#dialog').open"),10)
            if width<700:d.find_element(By.ID,'close-sidebar').click()
        saved=call('/chats/'+chat)['settings']
        assert saved['enable_thinking'] and saved['max_image_tokens']==16000
        assert saved['context_tokens']==35000 and saved['max_tokens']==12000
        assert saved['parallel_tool_calls'] is False
        errors=console_errors(d)
        assert not errors,errors
        assert not any(r['overflow'] for r in results),results
    record('flow-settings-ui',{'status':'PASS','settings':saved,'layouts':results})
    print('Thinking/image/context/output controls saved; three Firefox layouts PASS')
finally:
    call('/settings',original,'PUT')
