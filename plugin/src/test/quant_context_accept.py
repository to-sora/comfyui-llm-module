"""Check real uncached replies with optional system and tool context."""
import gzip
import json
import sys
from .engine_output import output
from .api_client import request
from .model_cases import TOOL
from .prefix_decode_cases import SYSTEM, message, correct

model, quant, precision = sys.argv[1:4]
cases = sys.argv[4:] or ['text', 'red', 'blue']
settings = {'model':model, 'quantization':quant, 'precision':precision,
            'kv_quantization':'hqq_8', 'prefix_cache':False,
            'temperature':0, 'max_tokens':64, 'enable_thinking':False}
target = output(f'quant-context-{model}-{quant}-{precision}.json.gz')
rows = []
for case in cases:
    for system in (False, True):
        for tools in (False, True):
            messages = [{'role':'system','content':SYSTEM}] if system else []
            body = {**settings, 'messages':messages+[message(case)]}
            if tools:
                body['tools'] = [TOOL]
            answer = request('/v1/chat/completions',body)['choices'][0]['message']
            row = {'case':case,'system':system,'tools':tools,'answer':answer,
                   'correct':correct(case,answer)}
            rows.append(row)
            target.write_bytes(gzip.compress(json.dumps({'settings':settings,'rows':rows},
                ensure_ascii=False,indent=2).encode()))
            print(case,'system',system,'tools',tools,row['correct'],answer,flush=True)
assert all(row['correct'] for row in rows),target
