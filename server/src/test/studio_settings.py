import time
from marionette_driver.by import By
from marionette_driver.keys import Keys
from browser_session import browser
from browser_helpers import until
from studio_helpers import call,record,snapshot,console_errors

original=call('/bootstrap')['settings']
chat=call('/chats',{})['id']
results=[]
started=time.monotonic()
try:
    with browser() as d:
        d.set_window_rect(width=1440,height=1000)
        d.navigate('https://127.0.0.1:8189/chats/'+chat)
        until(lambda:d.execute_script("return document.querySelectorAll('.suggestion').length===4"),30)
        for lang,theme,word in [('zh-Hant','dark','設定'),('zh-Hans','light','设置'),('en','system','Settings')]:
            d.find_element(By.ID,'settings').click()
            d.execute_script('''const f=document.querySelector('#dialog form');
                const fields={language:arguments[0],theme:arguments[1],model:'Qwen3.5-9B',
                  kv_quantization:'hqq_4',precision:'float16',context_tokens:8192,
                  max_tokens:512,image_checkpoint:'sd_xl_base_1.0.safetensors'};
                for(const [k,v] of Object.entries(fields))f.elements[k].value=v;
                f.elements.technical.checked=true;''',script_args=[lang,theme])
            d.find_element(By.CSS_SELECTOR,'#dialog button[type=submit]').click()
            until(lambda:d.execute_script("return !document.querySelector('#dialog').open&&document.documentElement.lang===arguments[0]",script_args=[lang]),30)
            assert d.find_element(By.ID,'settings').text==word
            if lang!='en':
                assert 'Attach a photo' not in d.find_element(By.ID,'empty').text
            results.append(snapshot(d,'settings-'+lang))
        d.navigate('https://127.0.0.1:8189/chats/'+chat)
        until(lambda:d.execute_script("return document.querySelectorAll('.suggestion').length===4"),30)
        saved=call('/chats/'+chat)['settings']
        assert saved['context_tokens']==8192 and saved['kv_quantization']=='hqq_4'
        assert saved['precision']=='float16' and saved['image_checkpoint']=='sd_xl_base_1.0.safetensors'
        d.find_element(By.ID,'debug').click()
        until(lambda:d.execute_script("return document.querySelector('#debug-panel').contains(document.activeElement)"),30)
        d.find_element(By.CSS_SELECTOR,'#debug-panel button').send_keys(Keys.ESCAPE)
        assert d.execute_script("return document.querySelector('#debug-panel').hidden&&!document.querySelector('#main').inert")
        errors=console_errors(d)
        assert not errors,errors
        assert not any(r['overflow'] for r in results)
    record('settings',{'status':'PASS','chat':chat,'layouts':results,'settings':saved,'seconds':time.monotonic()-started})
    print('Three languages, themes, assistant choices, refresh and Debug keyboard focus PASS')
finally:
    call('/settings',original,'PUT')
