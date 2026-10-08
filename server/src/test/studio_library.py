import tempfile
import time
from pathlib import Path
from marionette_driver.by import By
from browser_session import browser
from browser_helpers import until
from studio_helpers import ROOT,call,record,snapshot,console_errors
from studio_library_helpers import press,downloaded,select,upload,verify_downloads

started=time.monotonic()
with tempfile.TemporaryDirectory(dir=ROOT/'server/data/tmp') as folder,browser() as d:
    d.set_window_rect(width=1440,height=1000)
    d.navigate('https://127.0.0.1:8189/')
    until(lambda:d.execute_script("return document.querySelectorAll('.suggestion').length===4"),30)
    images=upload(d,Path(folder))
    d.find_element(By.CSS_SELECTOR,'.attachment button').click()
    assert d.execute_script("return document.querySelectorAll('.attachment').length===1")
    d.find_element(By.CSS_SELECTOR,'a[href="/library"]').click()
    first=images[0]['id']
    until(lambda:d.execute_script("return !!document.querySelector('[data-image=\"'+arguments[0]+'\"]')",script_args=[first]),30)
    d.find_element(By.CSS_SELECTOR,f'[data-image="{first}"]').click()
    until(lambda:d.execute_script("return !document.getElementById('viewer').hidden"),30)
    press(d,'☆ Favorite')
    until(lambda:call('/images/'+first+'/info')['favorite']==1,20)
    png=downloaded(lambda:d.find_element(By.CSS_SELECTOR,'#viewer a:not([href*="format="])').click(),'.png')
    jpg=downloaded(lambda:d.find_element(By.CSS_SELECTOR,'#viewer a[href*="format=jpg"]').click(),'.jpg')
    d.find_element(By.CSS_SELECTOR,'[aria-label="Close image viewer"]').click()
    for item in images: select(d,item['id'])
    archive=downloaded(lambda:press(d,'Download ZIP'),'.zip')
    result=verify_downloads(png,jpg,archive,images)
    snapshot(d,'library-downloads')
    press(d,'Use in new chat')
    until(lambda:d.execute_script("return location.pathname==='/'&&document.querySelectorAll('.attachment').length===2"),30)
    d.find_element(By.CSS_SELECTOR,'a[href="/library"]').click()
    until(lambda:d.execute_script("return document.querySelectorAll('.library-card').length>0"),30)
    for item in images: select(d,item['id'])
    press(d,'Delete');press(d,'Delete images')
    until(lambda:d.execute_script("return !document.getElementById('dialog').open"),30)
    assert all(r['id'] not in {v['id'] for v in call('/images')['images']} for r in images)
    assert not console_errors(d)
    for path in (png,jpg,archive): path.unlink()
record('library',{'status':'PASS',**result,'bulk_delete':True,'use_in_chat':True,'favorite':True,'seconds':time.monotonic()-started})
print('Firefox upload chips, PNG/JPG/ZIP downloads, favorites, use in chat and bulk delete PASS')
