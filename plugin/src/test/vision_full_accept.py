import gzip
import json
import sys
from pathlib import Path
from .api_client import request
from .model_cases import TOOL
from .prefix_decode_cases import message, correct

model = sys.argv[1] if len(sys.argv)>1 else 'Qwen3.5-9B-gguf'
rows = []
target = Path(__file__).resolve().parents[3]/f'fan-out/studio-engine/vision-full-{model}.json.gz'
for kv in ('none','hqq_8','hqq_4'):
    for system in (True,False):
        for case in ('white','yellow','photo'):
            messages = [{'role':'system','content':'Answer accurately from the actual image. Use tools only when needed.'}] if system else []
            messages.append(message(case))
            body = {'model':model,'quantization':'bnb_nf4','precision':'bfloat16',
                    'kv_quantization':kv,'prefix_cache':not system,'max_tokens':128,
                    'temperature':0,'enable_thinking':False,'messages':messages,'tools':[TOOL]}
            reply = request('/v1/chat/completions',body)['choices'][0]['message']
            profile = next(p for p in request('/llm/status')['models'] if p['model']==model
                           and p['quantization']=='bnb_nf4' and p['precision']=='bfloat16'
                           and p['kv_quantization']==kv)
            stats = profile['diagnostics']['prefix']
            row = {'kv':kv,'system':system,'prefix_requested':not system,
                   'case':case,'reply':reply,'cache':stats}
            rows.append(row)
            target.write_bytes(gzip.compress(json.dumps(rows,indent=2).encode()))
            assert correct(case,reply,''),row
            assert stats['last_reused_tokens']==0 and not stats['bypass_reason'],row
            assert stats['math_policy']==('mlp_fp32' if kv=='hqq_4' else 'mlp_down_fp32'),row
            print(kv,'system' if system else 'no system',case,'full prefill correct PASS',flush=True)
