"""Keep all actual replies while isolating convolution and delta kernels."""
import gzip
import json
import sys
from .api_client import request
from .engine_output import output
from .model_cases import TOOL
from .prefix_decode_cases import SYSTEM, message, correct

model, quant = sys.argv[1:3] or ['Qwen3.5-9B-gguf','bnb_nf4']
base = {'model':model,'quantization':quant,'precision':'bfloat16',
        'kv_quantization':'hqq_8','temperature':0,'max_tokens':128,
        'tools':[TOOL],'enable_thinking':False}
rows = []
target = output(f'kernel-modes-{model}-{quant}.json.gz')
for mode in ('reference','local','conv','delta'):
    cases = ['red','yellow','white','photo','vision_tool']
    for case in cases:
        messages = followup if case=='vision_tool_result' else [
            {'role':'system','content':SYSTEM},message(case)]
        prior = '\n'.join(m.get('content') or '' for m in messages if m['role']=='assistant')
        for repeat in range(2):
            answer = request('/v1/chat/completions',{
                **base,'messages':messages,'diagnostic_kernels':mode})['choices'][0]['message']
            profile = next(p for p in request('/llm/status')['models']
                if all(p[k]==base[k] for k in ('model','quantization','precision','kv_quantization')))
            passed = correct(case,answer,prior)
            rows.append({'mode':mode,'case':case,'repeat':repeat,'answer':answer,
                         'correct':passed,'diagnostics':profile['diagnostics']})
            target.write_bytes(gzip.compress(json.dumps(rows,ensure_ascii=False,indent=2).encode()))
            print(mode,case,repeat,passed,flush=True)
            assert profile['diagnostics']['kernel_mode']==mode
            assert profile['diagnostics']['prefix']['kernel_policy']==mode
        if case=='vision_tool' and passed:
            followup = messages+[answer,{'role':'tool','tool_call_id':answer['tool_calls'][0]['id'],
                'content':'{"city":"Hong Kong","temperature_c":21,"condition":"cloudy"}'}]
            cases.append('vision_tool_result')
print({m:sum(r['correct'] for r in rows if r['mode']==m) for m in ('reference','local','conv','delta')})
