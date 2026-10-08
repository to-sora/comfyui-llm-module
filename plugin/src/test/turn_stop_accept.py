import gzip
import json
import sys
from pathlib import Path
from .api_client import request
from .model_cases import TOOL, MEMORY_SYSTEM, user
from .prefix_decode_cases import message

model = sys.argv[1] if len(sys.argv)>1 else 'Qwen3.5-9B'
rows = []
cases = [('vision_tool',message('vision_tool'),{'Hong Kong'}),
         ('parallel',user('Get the current weather for both Paris and London.'),{'Paris','London'})]
for name, question, cities in cases:
    body = {'model':model,'quantization':'bnb_nf4','kv_quantization':'hqq_8',
            'temperature':0,'enable_thinking':False,'max_tokens':128,
            'parallel_tool_calls':True,'tools':[TOOL],
            'messages':[{'role':'system','content':MEMORY_SYSTEM},question]}
    if model.startswith('Qwen'):
        body['diagnostic_prefix'] = 'default'
        body['prefix_cache'] = False
    reply = request('/v1/chat/completions',body)
    answer = reply['choices'][0]['message']
    calls = [c['function'] for c in answer.get('tool_calls',[])]
    assert len(calls)==len(cities) and all(c['name']=='get_weather' for c in calls),reply
    assert {json.loads(c['arguments'])['city'] for c in calls}==cities,reply
    row = {'case':name,'reply':reply}
    if model.startswith('Qwen'):
        profile = next(p for p in request('/llm/status')['models']
                       if p['model']==model and p['kv_quantization']=='hqq_8')
        row['decode'] = profile['diagnostics']['prefix_probe']['decode']
        for run in row['decode']['runs']:
            assert run['raw'].endswith('<|im_end|>') and run['raw'].count('<|im_end|>')==1,run
            assert '<|im_start|>' not in run['raw'] and '<tool_response>' not in run['raw'],run
            assert {json.loads(c['arguments'])['city'] for c in run['tools']}==cities,run
    rows.append(row)
    path = Path(__file__).resolve().parents[3]/f'fan-out/studio-engine/turn-stop-{model}.json.gz'
    path.write_bytes(gzip.compress(json.dumps(rows,ensure_ascii=False,indent=2).encode()))
    print(model,name,'actual turn end and requested tools PASS',flush=True)
