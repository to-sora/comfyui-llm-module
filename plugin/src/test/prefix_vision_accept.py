import gzip
import json
import sys
import time
from pathlib import Path
from .api_client import request
from .model_cases import TOOL
from .prefix_decode_cases import message, correct

model = sys.argv[1] if len(sys.argv)>1 else 'Qwen3.5-9B'
system = 'You are a concise, accurate assistant. Answer the user using the conversation and actual image contents. Use an available tool when current information is needed. Never invent tool results. Follow the requested reply format, and distinguish visible facts from guesses.'
base = {'model':model,'quantization':'bnb_nf4','kv_quantization':'hqq_8',
        'temperature':0,'max_tokens':128,'tools':[TOOL],'enable_thinking':False}
system = {'role':'system','content':system}
target = Path(__file__).resolve().parents[3]/f'fan-out/studio-engine/prefix-live-{model}.json.gz'
rows = []


def run(messages, policy):
    started = time.monotonic()
    answer = request('/v1/chat/completions',{**base,'messages':messages})
    profile = next(p for p in request('/llm/status')['models']
                   if p['model']==model and p['kv_quantization']=='hqq_8')
    stats = profile['diagnostics']['prefix']
    assert stats['math_policy']==policy and not stats['bypass_reason'],stats
    return {'reply':answer['choices'][0]['message'],'cache':stats,
            'seconds':time.monotonic()-started,'loads':profile['loads']}


text = [system,{'role':'user','content':'What is 17 + 25?'}]
run(text,'default')
cases = ['red','green','blue','yellow','white','black','photo','multi','vision_tool']
for case in cases:
    messages = followup if case=='vision_tool_result' else [system,message(case)]
    prior = '\n'.join(m.get('content') or '' for m in messages if m['role']=='assistant')
    values = [run(messages,'mlp_down_fp32') for _ in range(2)]
    row = {'case':case,'runs':values,'prior_assistant_text':prior}
    rows.append(row)
    target.write_bytes(gzip.compress(json.dumps(rows,ensure_ascii=False,indent=2).encode()))
    assert all(correct(case,v['reply'],prior) for v in values),row
    assert values[-1]['cache']['last_reused_tokens']>=64,row
    if case=='vision_tool':
        answer = values[-1]['reply']
        followup = messages+[answer,{'role':'tool','tool_call_id':answer['tool_calls'][0]['id'],
            'content':'{"city":"Hong Kong","temperature_c":21,"condition":"cloudy"}'}]
        cases.append('vision_tool_result')
    print(model,case,'production prefix hit and correct result PASS',flush=True)
last = run(text,'default')
assert last['cache']['last_reused_tokens']>=64,last
print(model,'text and vision cache entries remain separate PASS',flush=True)
