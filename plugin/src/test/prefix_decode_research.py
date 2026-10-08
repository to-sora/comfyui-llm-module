import gzip
import json
import sys
import time
from pathlib import Path
from .api_client import request
from .model_cases import TOOL
from .prefix_decode_cases import message as input_message

model = sys.argv[1] if len(sys.argv)>1 else 'Qwen3.5-9B-gguf'
kv = sys.argv[2] if len(sys.argv)>2 else 'none'
color = sys.argv[3] if len(sys.argv)>3 else 'yellow'
system = 'You are a concise, accurate assistant. Answer the user using the conversation and actual image contents. Use an available tool when current information is needed. Never invent tool results. Follow the requested reply format, and distinguish visible facts from guesses.'
body = {'model':model,'kv_quantization':kv,'quantization':'bnb_nf4','max_tokens':64,
        'prefix_cache':False,
        'temperature':0,'tools':[TOOL],'enable_thinking':False,
        'messages':[{'role':'system','content':system},input_message(color)]}
rows = []
target = Path(__file__).resolve().parents[3]/'fan-out/studio-engine'
modes = sys.argv[4:] or ('default','full_accumulation','math_attention','fixed_reduction')
suffix = '-'+ '-'.join(sys.argv[4:]) if sys.argv[4:] else ''
for mode in modes:
    started = time.monotonic()
    reply = request('/v1/chat/completions',{**body,'diagnostic_prefix':mode})
    message = reply['choices'][0]['message']
    content = message.get('content','').lower()
    correct = any(word in content for word in ('cup','mug')) if color=='photo' else content==color
    assert correct and not message.get('tool_calls'),reply
    state = request('/llm/status')
    profile = next(p for p in state['models'] if p['model']==model and p['kv_quantization']==kv)
    probe = profile['diagnostics']['prefix_probe']
    decode = probe['decode']
    assert len(decode['runs'])==3 and decode['prefix_tokens']>=64,decode
    assert decode['runs'][1]['tokens']==decode['runs'][2]['tokens'],decode
    rows.append({'mode':mode,'seconds':time.monotonic()-started,
                 'production_reply':message,'decode':decode,'logit_max':probe['logit_max']})
    (target/f'prefix-decode-{model}-{kv}-{color}{suffix}.json.gz').write_bytes(
        gzip.compress(json.dumps(rows,ensure_ascii=False,indent=2).encode()))
    print(mode,[(r['path'],r['content'],r['tools']) for r in decode['runs']],
          'equivalent:',decode['messages_equal'],flush=True)
