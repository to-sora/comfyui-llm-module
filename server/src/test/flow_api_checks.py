import json
from pathlib import Path


def call(reply,stage,pair,caps):
    choice=reply['choices'][0]
    message=choice['message']
    calls=message.get('tool_calls',[])
    assert len(calls)==1 and calls[0]['function']['name']=='generate_images',message
    args=json.loads(calls[0]['function']['arguments'])
    assert len(args['images'])==(1 if stage==2 else 2),args
    names={i.get('checkpoint',args.get('checkpoint')) for i in args['images']}
    assert names<=set(caps['batch_checkpoints']),names
    assert len(names)==(1 if stage==2 else 2),names
    if stage>1:assert names<=set(pair),(names,pair)
    assert reply['usage']['completion_tokens_details']['reasoning_tokens']>0,reply['usage']
    if stage>1:assert reply['usage']['image_tokens'],reply['usage']
    return message,args,sorted(names)


def resident(status,profile):
    owners=[m for m in status['models'] if m['in_ram']]
    assert len(owners)==1 and owners[0]['model']==profile,owners
    assert owners[0]['loads']==1,owners
    assert all(v['reads']==1 for v in status['weight_reads'].values()
               if v['purpose']!='SDXL checkpoint'),status['weight_reads']
    return owners[0]


def counts(status,pair):
    entries=status['checkpoints']['resident']
    assert set(pair)<={Path(e['source']).name for e in entries},entries
    return {Path(k).name:v['reads'] for k,v in status['weight_reads'].items() if Path(k).name in pair}
