import json
import re
import ssl
import subprocess
import time
import urllib.request
from studio_helpers import ROOT,call
from browser_helpers import until


def finished(ident):
    run=call('/debug/runs/'+ident)
    return run if run['status'] not in ('running','queued') else None


def restart():
    subprocess.run([str(ROOT/'server/start.sh'),'--stop'],cwd=ROOT,check=True,timeout=20)
    with (ROOT/'server/data/recovery-start.log').open('ab') as log:
        subprocess.Popen([str(ROOT/'server/start.sh')],cwd=ROOT,stdout=log,
                         stderr=subprocess.STDOUT,start_new_session=True)
    def ready():
        try:
            return call('/bootstrap')['connected']
        except (OSError,ValueError):
            return False
    until(ready,60)


def drawing():
    with urllib.request.urlopen('https://127.0.0.1:8188/queue',context=ssl._create_unverified_context()) as r:
        queue=json.load(r)
    return any(any(n['class_type']=='SamplerCustomAdvanced' for n in item[2].values()) for item in queue['queue_running'])


def same_text(d,chat):
    rows=call('/chats/'+chat+'/messages')['messages']
    expected=''.join(p['text'] for m in rows if m['role']=='assistant' for p in m['parts'] if p['type']=='text')
    actual=d.execute_script("return [...document.querySelectorAll('.assistant .message-content')].map(n=>n.textContent).join('')")
    clean=lambda value:re.sub(r'\s+','',value)
    assert clean(actual)==clean(expected),(len(actual),len(expected),actual[-80:],expected[-80:])
    return len(expected)
