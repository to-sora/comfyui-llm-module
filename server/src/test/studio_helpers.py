import base64
import gzip
import json
import ssl
import urllib.request
from contextlib import contextmanager
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'fan-out/studio-chat'
OUT.mkdir(parents=True,exist_ok=True)


@contextmanager
def saved_settings():
    original=call('/bootstrap')['settings']
    try:
        yield
    finally:
        call('/settings',original,'PUT')


def call(path,body=None,method=None):
    request=urllib.request.Request('https://127.0.0.1:8189/api'+path,
        data=None if body is None else json.dumps(body).encode(),
        headers={'Content-Type':'application/json'},method=method)
    with urllib.request.urlopen(request,context=ssl._create_unverified_context(),timeout=30) as response:
        return json.load(response)


def record(name,value):
    raw=json.dumps(value,ensure_ascii=False,indent=2).encode()
    if len(raw)>3000:
        (OUT/(name+'.json.gz')).write_bytes(gzip.compress(raw))
    else:
        (OUT/(name+'.json')).write_bytes(raw)


def snapshot(driver,name):
    (OUT/(name+'.png')).write_bytes(base64.b64decode(driver.screenshot()))
    return driver.execute_script('return {width:innerWidth,height:innerHeight,overflow:document.documentElement.scrollWidth>innerWidth||document.documentElement.scrollHeight>innerHeight+1}')


def console_errors(driver):
    with driver.using_context(driver.CONTEXT_CHROME):
        return driver.execute_script("return Services.console.getMessageArray().map(m=>m.message).filter(x=>x.includes('8189')&&x.includes('Error'))")
