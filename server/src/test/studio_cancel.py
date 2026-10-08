import json
import ssl
import time
import urllib.request
from studio_helpers import call,record


def queue():
    with urllib.request.urlopen('https://127.0.0.1:8188/queue',context=ssl._create_unverified_context()) as r:
        return json.load(r)


chat=call('/chats',{})
sent=call('/chats/'+chat['id']+'/messages',{'text':
    'Make four different landscape photographs: mountains, forest, beach, and desert.',
    'attachments':[]})
for _ in range(180):
    value=queue()
    running=value['queue_running']
    if running and any(n['class_type']=='SamplerCustomAdvanced' for n in running[0][2].values()):
        break
    time.sleep(.2)
else:
    raise AssertionError('No active SDXL work was observed')
before=call('/debug/runs/'+sent['run_id'])
started=time.monotonic()
call('/runs/'+sent['run_id']+'/cancel',{})
for _ in range(100):
    run=call('/debug/runs/'+sent['run_id'])
    if run['status']=='cancelled':
        break
    time.sleep(.2)
assert run['status']=='cancelled',run['status']
own=set(run['trace']['prompt_ids'])
for _ in range(100):
    pending=queue()
    if not any(row[1] in own for row in pending['queue_running']+pending['queue_pending']):
        break
    time.sleep(.1)
assert not any(row[1] in own for row in pending['queue_running']+pending['queue_pending'])
native_seconds=time.monotonic()-started
follow=call('/chats/'+chat['id']+'/messages',{'text':'What is 6 times 7? Reply with only the number.','attachments':[]})
for _ in range(90):
    result=call('/debug/runs/'+follow['run_id'])
    if result['status'] not in ('running','queued'):
        break
    time.sleep(1)
record('cancel',{'before':before,'cancelled':run,'following':result})
assert result['status']=='done',result.get('error')
answer=[s['response']['content'] for s in result['trace']['steps'] if s['kind']=='assistant'][-1]
assert answer.strip()=='42',answer
record('cancel-result',{'passed':True,'chat':chat['id'],'native_work_remaining':False,
    'following_answer':answer,'native_cancel_seconds':round(native_seconds,2),
    'seconds_including_followup':round(time.monotonic()-started,2)})
print('Multiple native prompts cancelled; following reply is 42',flush=True)
