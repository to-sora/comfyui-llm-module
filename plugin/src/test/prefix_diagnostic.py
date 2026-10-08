import gzip
import json
import sys
import time
from pathlib import Path
from .api_client import request
from .model_cases import TOOL, image_message

model = sys.argv[1] if len(sys.argv)>1 else 'Qwen3.5-9B-gguf'
system = 'You are a concise, accurate assistant. Answer the user using the conversation and actual image contents. Use an available tool when current information is needed. Never invent tool results. Follow the requested reply format, and distinguish visible facts from guesses.'
body = {'model':model,'kv_quantization':'none','quantization':'bnb_nf4','max_tokens':32,
        'temperature':0,'tools':[TOOL],'enable_thinking':False,
        'messages':[{'role':'system','content':system},image_message('yellow')]}
rows = []
for mode in ('default','full_accumulation','math_attention','fixed_reduction'):
    started = time.monotonic()
    reply = request('/v1/chat/completions',{**body,'diagnostic_prefix':mode})
    message = reply['choices'][0]['message']
    assert message.get('content','').lower() == 'yellow' and not message.get('tool_calls'),reply
    state = request('/llm/status')
    profile = next(p for p in state['models'] if p['model']==model and p['kv_quantization']=='none')
    values = profile['diagnostics']['prefix_probe']
    rows.append({'seconds':time.monotonic()-started,'reply':reply,'probe':values})
    first = next((r for r in values['layers'] if r['prefix_max']),None)
    print(mode, 'logit max',values['logit_max'],'first divergent prefix',first,flush=True)
    target = Path(__file__).resolve().parents[3]/'fan-out/studio-engine'
    (target/f'prefix-diagnostic-{model}.json.gz').write_bytes(gzip.compress(json.dumps(rows,indent=2).encode()))
