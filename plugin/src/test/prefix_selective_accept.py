import gzip
import json
import os
import sys
from .engine_output import output
from .api_client import request
from .model_cases import TOOL
from .prefix_decode_cases import message, correct, SYSTEM as system

model, kv, mode = (sys.argv[1:4] or ['Qwen3.5-9B-gguf', 'hqq_8', 'mlp_down_fp32'])
quant = os.environ.get('PREFIX_TEST_QUANTIZATION','bnb_nf4')
precision = os.environ.get('PREFIX_TEST_PRECISION','bfloat16')
system = os.environ.get('PREFIX_TEST_SYSTEM',system)
cases = list(sys.argv[4:] or ('red','green','blue','yellow','black','white','photo','multi','vision_tool'))
rows = []
path = output(f'prefix-selective-{model}-{kv}-{mode}.json.gz')
if (quant,precision) != ('bnb_nf4','bfloat16'):
    path = path.with_name(path.name.replace('.json.gz','-'+quant+'-'+precision+'.json.gz'))
if sys.argv[4:]:
    path = path.with_name(path.name.replace('.json.gz','-'+'-'.join(cases)+'.json.gz'))
if 'PREFIX_TEST_SYSTEM' in os.environ:
    path = path.with_name(path.name.replace('.json.gz','-custom-system.json.gz'))


for case in cases:
    messages = followup if case == 'vision_tool_result' else [{'role':'system','content':system},message(case)]
    prior = '\n'.join(m.get('content') or '' for m in messages if m['role']=='assistant')
    body = {'model':model,'kv_quantization':kv,'quantization':quant,'precision':precision,'max_tokens':64,
            'prefix_cache':False,
            'temperature':0,'tools':[TOOL],'enable_thinking':False,'diagnostic_prefix':mode,
            'messages':messages}
    result = request('/v1/chat/completions', body)['choices'][0]['message']
    state = request('/llm/status')
    profile = next(p for p in state['models'] if p['model']==model and p['kv_quantization']==kv
                   and p['quantization']==quant and p['precision']==precision)
    decode = profile['diagnostics']['prefix_probe']['decode']
    for value in decode['runs']:
        value['correct'] = correct(case, value, prior)
    row = {'case':case,'system':system,'prior_assistant_text':prior,'normal_reply':result,
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
