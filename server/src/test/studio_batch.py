import time
from studio_helpers import call,record

chat=call('/chats',{})
result=call('/chats/'+chat['id']+'/messages',{'text':
    'Make two variations using exactly the same description: a single yellow teapot centered on a plain white background. Check the results.',
    'attachments':[]})
for _ in range(300):
    run=call('/debug/runs/'+result['run_id'])
    if run['status'] not in ('queued','running'):
        break
    time.sleep(1)
value=call('/chats/'+chat['id']+'/messages')
record('same-prompt-batch',{'run':run,'messages':value})
assert run['status']=='done',run.get('error')
images=[i for i in value['images'].values() if i['file'] and i['kind']=='generated']
assert len(images)==2,images
assert len({i['recipe']['prompt_id'] for i in images})==1,'Identical variations did not use one native batch'
assert len({i['recipe']['seed'] for i in images})==2
assert len({i['sha256'] for i in images})==2
assert all(len(i['recipe']['batch_seeds'])==2 for i in images)
record('same-prompt-result',{'passed':True,'chat':chat['id'],
    'prompt_id':images[0]['recipe']['prompt_id'],'seeds':[i['recipe']['seed'] for i in images],
    'different_images':True,'batch_indices':[i['recipe']['batch_index'] for i in images]})
print('Same prompt: one ComfyUI batch, two distinct seeds and images',flush=True)
