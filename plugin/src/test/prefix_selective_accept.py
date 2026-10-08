import gzip
import json
import sys
from pathlib import Path
from .api_client import request
from .model_cases import TOOL
from .prefix_decode_cases import message, correct

model, kv, mode = (sys.argv[1:4] or ['Qwen3.5-9B-gguf', 'hqq_8', 'mlp_down_fp32'])
cases = list(sys.argv[4:] or ('red','green','blue','yellow','black','white','photo','multi','vision_tool'))
system = 'You are a concise, accurate assistant. Answer the user using the conversation and actual image contents. Use an available tool when current information is needed. Never invent tool results. Follow the requested reply format, and distinguish visible facts from guesses.'
rows = []
path = Path(__file__).resolve().parents[3]/f'fan-out/studio-engine/prefix-selective-{model}-{kv}-{mode}.json.gz'
if sys.argv[4:]:
    path = path.with_name(path.name.replace('.json.gz','-'+'-'.join(cases)+'.json.gz'))


for case in cases:
    messages = followup if case == 'vision_tool_result' else [{'role':'system','content':system},message(case)]
    prior = '\n'.join(m.get('content') or '' for m in messages if m['role']=='assistant')
    body = {'model':model,'kv_quantization':kv,'quantization':'bnb_nf4','max_tokens':64,
            'prefix_cache':False,
            'temperature':0,'tools':[TOOL],'enable_thinking':False,'diagnostic_prefix':mode,
            'messages':messages}
    result = request('/v1/chat/completions', body)['choices'][0]['message']
    state = request('/llm/status')
    profile = next(p for p in state['models'] if p['model']==model and p['kv_quantization']==kv)
    decode = profile['diagnostics']['prefix_probe']['decode']
    for value in decode['runs']:
        value['correct'] = correct(case, value, prior)
    row = {'case':case,'prior_assistant_text':prior,'normal_reply':result,
           'normal_correct':correct(case,result,prior),'decode':decode}
    rows.append(row)
    path.write_bytes(gzip.compress(json.dumps(rows,ensure_ascii=False,indent=2).encode()))
    print(case,'normal',row['normal_correct'],[(r['path'],r['correct']) for r in decode['runs']],flush=True)
    if case == 'vision_tool' and result.get('tool_calls'):
        call = result['tool_calls'][0]
        followup = messages + [result, {'role':'tool','tool_call_id':call['id'],
            'content':'{"city":"Hong Kong","temperature_c":21,"condition":"cloudy"}'}]
        cases.append('vision_tool_result')
assert all(all(v['correct'] for v in r['decode']['runs']) for r in rows),path
