import json
import sys
import time
import re
from pathlib import Path
from .api_client import request
from .model_cases import TOOL,user,image_message

model=sys.argv[1] if len(sys.argv)>1 else 'Qwen3.5-9B'
mode=sys.argv[2] if len(sys.argv)>2 else 'hqq_8'
system={'role':'system','content':'You are a concise, accurate assistant. Answer the user using the conversation and actual image contents. Use an available tool when current information is needed. Never invent tool results. Follow the requested reply format, and distinguish visible facts from guesses.'}
base={'model':model,'kv_quantization':mode,'quantization':'bnb_nf4','max_tokens':100,'temperature':0,
      'tools':[TOOL],'enable_thinking':False}
cases=[('text',[user('What is 17 + 25? Reply with only the number.')],{}),
       ('blue',[image_message('blue')],{}),('yellow',[image_message('yellow')],{}),
       ('tool',[user('What is the weather in Hong Kong?')],{'tool_choice':'required'})]
evidence=[]

def clean(reply):
    message=reply['choices'][0]['message']
    return {'content':message.get('content'),
            'tools':[call['function'] for call in message.get('tool_calls',[])]}

for name,messages,extra in cases:
    body={**base,**extra,'messages':[system]+messages}
    values=[]
    for enabled in (False,True,True):
        started=time.monotonic()
        response=request('/v1/chat/completions',{**body,'prefix_cache':enabled})
        state=request('/llm/status')
        profile=next(p for p in state['models'] if p['model']==model and p['kv_quantization']==mode)
        values.append({'seconds':time.monotonic()-started,'reply':clean(response),
                       'cache':profile['diagnostics'].get('prefix',{})})
    assert values[0]['reply']==values[1]['reply']==values[2]['reply'],(name,values)
    bypass=values[2]['cache'].get('bypass_reason')
    assert values[2]['cache']['last_reused_tokens']>=32 or (
        name in ('blue','yellow') and bypass=='hybrid_vision_full_prefill'),values
    if name=='text':
        assert re.findall(r'\d+',values[0]['reply']['content'])[-1]=='42'
    if name in ('blue','yellow'): assert name in values[0]['reply']['content'].lower()
    if name=='tool': assert values[0]['reply']['tools'][0]['name']=='get_weather'
    evidence.append({'case':name,'runs':values,
        'number_only_format':values[0]['reply']['content'].strip()=='42' if name=='text' else None})
    print(model,mode,name,'equivalent;',bypass or 'actual prefix hit','PASS',flush=True)
output=Path(__file__).resolve().parents[3]/'fan-out/studio-engine'
import gzip
(output/f'prefix-{model}-{mode}.json.gz').write_bytes(gzip.compress(json.dumps(evidence,indent=2).encode()))
