import json
import time
import uuid
import sys
from plugin.src.test.api_client import request
from .studio_helpers import record
from .ram_observer import Observer,comfy
from . import flow_api_prompt as prompt,flow_api_checks as check
from .flow_api_llm import invoke
from .flow_api_images import generate


def execute(profile,index,previous,pid,caps,messages):
    token='flow-api-'+uuid.uuid4().hex
    shared=token+'-shared'
    observer=Observer(pid)
    started=time.monotonic()
    result={'pid':pid,'profile':profile,'round':index,'before':comfy('/llm/status'),'steps':[]}
    pair=[];images=[];baseline=None
    try:
        for stage in (1,2,3):
            observer.phase=f'{profile}/{index}/LLM{stage}'
            messages.append(prompt.user(index,stage,pair,previous,images))
            reply,message,args,names=invoke(profile,messages,caps,pair,stage,observer,result)
            messages.append(message)
            if stage==1:
                pair=names
                request('/llm/turns/'+token,{'checkpoints':pair},method='PUT')
            observer.phase=f'{profile}/{index}/SDXL{stage}'
            images=generate(caps,args,token,stage,observer,start=(index-1)*5+{1:1,2:3,3:4}[stage])
            status=comfy('/llm/status')
            check.resident(status,profile)
            current=check.counts(status,pair)
            if baseline is None:baseline=current
            assert current==baseline,(current,baseline)
            result['steps'].append({'reply':reply,'images':images,'status':status})
            messages.append({'role':'tool','tool_call_id':message['tool_calls'][0]['id'],
                'content':json.dumps({'images':[{k:i[k] for k in ('image','checkpoint','prompt')} for i in images]})})
            prompt.compact(messages)
            if stage==1 and index==1:
                request('/llm/turns/'+shared,{'checkpoints':pair},method='PUT')
                result['sharing']=generate(caps,{**args,'images':args['images'][:1]},shared,0,observer)
        request('/llm/turns/'+token,method='DELETE')
        after=comfy('/llm/status')
        if index==1:
            assert check.counts(after,pair)==baseline
            assert all(shared in e['turns'] for e in after['checkpoints']['resident'])
        result.update(status='PASS',pair=pair,after=after)
        return result
    finally:
        if sys.exc_info()[1]:result['error']=str(sys.exc_info()[1])
        request('/llm/turns/'+token,method='DELETE')
        request('/llm/turns/'+shared,method='DELETE')
        result.update(seconds=time.monotonic()-started,observation=observer.close())
        record(f'flow-api-{profile}-{index:02}',result)
        print(profile,index,result.get('status','FAIL'),round(result['seconds'],1),pair,flush=True)
