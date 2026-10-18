import time
from server.src.test.studio_helpers import call,record


def restore(observer):
    original=call('/bootstrap')['settings']
    chat=call('/chats',{})['id']
    call('/chats/'+chat,{'title':'Retained 9B and SDXL baseline for 27B'},'PATCH')
    preferences={**original,'chat_id':chat,'assistant':{**original['assistant'],
        'model':'Qwen3.5-9B','quantization':'bnb_nf4','precision':'bfloat16',
        'kv_quantization':'hqq_8','context_tokens':8192,'max_tokens':256}}
    observer.phase='restore retained 9B + SDXL baseline'
    try:
        call('/settings',preferences,'PUT')
        result=call('/chats/'+chat+'/messages',{'text':
            'Generate one studio photo of a red ceramic mug on a plain white background. Inspect it briefly.',
            'attachments':[]})
        started=time.monotonic()
        while time.monotonic()-started<600:
            run=call('/debug/runs/'+result['run_id'])
            if observer.low:
                call('/runs/'+run['id']+'/cancel',{})
                raise MemoryError('Baseline reached the planning safety threshold')
            if run['status'] not in ('queued','running'):
                record('e2e-27b-baseline-261019',{'chat':chat,'run':run,'seconds':time.monotonic()-started})
                if run['status']!='done':raise RuntimeError(run['error'])
                print('Retained baseline ready:',chat,round(time.monotonic()-started,2),flush=True)
                return
            time.sleep(1)
        call('/runs/'+result['run_id']+'/cancel',{})
        raise TimeoutError('Baseline did not finish')
    finally:call('/settings',original,'PUT')
