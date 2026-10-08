import gzip
import json
import os
import sys
from .engine_output import output
from .api_client import request
from .model_cases import TOOL
from .prefix_decode_cases import message, correct

model = sys.argv[1] if len(sys.argv)>1 else 'Qwen3.5-9B-gguf'
quant = os.environ.get('PREFIX_TEST_QUANTIZATION','bnb_nf4')
precision = os.environ.get('PREFIX_TEST_PRECISION','bfloat16')
rows = []
target = output(f'vision-full-{model}.json.gz')
if (quant,precision) != ('bnb_nf4','bfloat16'):
    target = target.with_name(target.name.replace('.json.gz','-'+quant+'-'+precision+'.json.gz'))
for kv in ('none','hqq_8','hqq_4'):
    for system in (True,False):
        for case in ('white','yellow','photo'):
            messages = [{'role':'system','content':'Answer accurately from the actual image. Use tools only when needed.'}] if system else []
            messages.append(message(case))
            body = {'model':model,'quantization':quant,'precision':precision,
                    'kv_quantization':kv,'prefix_cache':not system,'max_tokens':128,
                    'temperature':0,'enable_thinking':False,'messages':messages,'tools':[TOOL]}
            reply = request('/v1/chat/completions',body)['choices'][0]['message']
            profile = next(p for p in request('/llm/status')['models'] if p['model']==model
                           and p['quantization']==quant and p['precision']==precision
                           and p['kv_quantization']==kv)
            stats = profile['diagnostics']['prefix']
            row = {'kv':kv,'system':system,'prefix_requested':not system,
                   'case':case,'reply':reply,'cache':stats,'correct':correct(case,reply,'')}
            rows.append(row)
            target.write_bytes(gzip.compress(json.dumps(rows,indent=2).encode()))
            assert stats['last_reused_tokens']==0 and not stats['bypass_reason'],row
            assert stats['math_policy']==('mlp_fp32' if kv=='hqq_4' else 'mlp_down_fp32'),row
            print(kv,'system' if system else 'no system',case,'correct',row['correct'],flush=True)
assert all(row['correct'] for row in rows),target
