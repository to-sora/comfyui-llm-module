import ssl
import time
import urllib.request
from studio_helpers import call,record,OUT

original=call('/bootstrap')['settings']
models=[p['id'] for p in call('/bootstrap')['profiles']]
evidence=[]

def wait(ident):
    for _ in range(1200):
        run=call('/debug/runs/'+ident)
        if run['status'] not in ('queued','running'):
            assert run['status']=='done',(run['settings']['model'],run.get('error'),run['trace'])
            return run
        time.sleep(.5)
    raise TimeoutError('Model workflow did not finish')

try:
    for model in models:
        chat=call('/chats',{})['id']
        config={**original['assistant'],'model':model,'precision':'bfloat16',
                'context_tokens':16384,'kv_quantization':'hqq_8','quantization':'default'}
        call('/settings',{**original,'assistant':config,'chat_id':chat},'PUT')
        sent=call('/chats/'+chat+'/messages',{'text':
            'Make a studio photograph of one red ceramic mug on a plain white background. Check the finished picture and describe what you can actually see.',
            'attachments':[]})
        run=wait(sent['run_id'])
        page=call('/chats/'+chat+'/messages')
        images=[i for i in page['images'].values() if i['kind']=='generated' and i['file']]
        assert len(images)==1,(model,images)
        image=images[0]
        assert image['recipe']['assistant']['model']==model,image['recipe']
        steps=run['trace']['steps']
        requests=[s['body'] for s in steps if s['kind']=='request']
        assert len(requests)>=2
        assert any(isinstance(m.get('content'),list) and any(p['type']=='image_url' for p in m['content']) for m in requests[-1]['messages'])
        follow=call('/chats/'+chat+'/messages',{'text':'What is the main object and its color in this picture? Answer briefly without changing it.','attachments':[image['id']]})
        review=wait(follow['run_id'])
        answer=[s['response']['content'] for s in review['trace']['steps'] if s['kind']=='assistant'][-1]
        record('profile-'+model,{'generated':run,'reviewed':review,'image':image})
        with urllib.request.urlopen('https://127.0.0.1:8189/api/images/'+image['id'],context=ssl._create_unverified_context()) as response:
            (OUT/('profile-'+model+'.png')).write_bytes(response.read())
        evidence.append({'model':model,'chat':chat,'image':image['id'],'seed':image['recipe']['seed'],'answer':answer})
        record('profiles',evidence)
        print(model,answer,flush=True)
finally:
    call('/settings',original,'PUT')
