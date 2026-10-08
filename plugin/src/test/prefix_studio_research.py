import gzip
import json
import sys
import time
from pathlib import Path
from .api_client import request

root = Path(__file__).resolve().parents[3]/'fan-out'
fixture = json.loads(gzip.decompress((root/'studio-chat/engine-recheck.json.gz').read_bytes()))
requests = [s['body'] for s in fixture['run']['trace']['steps'] if s['kind']=='request']
model = sys.argv[1] if len(sys.argv)>1 else 'Qwen3.5-9B-gguf'
kv = sys.argv[2] if len(sys.argv)>2 else 'hqq_8'
body = {**requests[-1],'model':model,'quantization':'bnb_nf4',
        'kv_quantization':kv,'max_tokens':64,'temperature':0,'enable_thinking':False,'stream':False}
body.pop('max_completion_tokens',None)
rows = []
for mode in sys.argv[3:] or ('default','fp32_default_attention'):
    started = time.monotonic()
    reply = request('/v1/chat/completions',{**body,'diagnostic_prefix':mode})
    message = reply['choices'][0]['message']
    assert any(w in message.get('content','').lower() for w in ('cup','mug')),reply
    assert not message.get('tool_calls'),reply
    state = request('/llm/status')
    profile = next(p for p in state['models'] if p['model']==model and p['kv_quantization']==kv)
    probe = profile['diagnostics']['prefix_probe']
    decode = probe['decode']
    assert decode['timing_includes_cache_setup'] and len(decode['runs'])==3,decode
    assert decode['runs'][1]['tokens']==decode['runs'][2]['tokens'],decode
    rows.append({'mode':mode,'source_chat':fixture['chat'],'source_image':fixture['image']['id'],
                 'production_reply':message,'seconds':time.monotonic()-started,'decode':decode})
    suffix = '-'+ '-'.join(sys.argv[3:]) if sys.argv[3:] else ''
    (root/f'studio-engine/prefix-studio-{model}-{kv}{suffix}.json.gz').write_bytes(
        gzip.compress(json.dumps(rows,ensure_ascii=False,indent=2).encode()))
    print(mode,'prefix',decode['prefix_tokens'],[(r['path'],round(r['seconds'],3),
          r['content'],r['tools']) for r in decode['runs']],flush=True)
