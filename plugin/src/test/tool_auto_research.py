"""Compare optional-tool guidance with real text, image and tool replies."""
import gzip
import json
from .engine_output import output
from .api_client import request
from .model_cases import TOOL
from .prefix_decode_cases import SYSTEM, message, correct

GUIDANCE = ("Tools are optional. Use a tool only when its documented capability is needed "
            "to satisfy the user's request. Otherwise answer directly from the conversation "
            "and image contents. Tool availability alone is not a reason to call it.")
target = output('tool-auto-research.json.gz')
rows = []
for model,quant,precision in (('Qwen3.5-9B','bnb_fp4','bfloat16'),
        ('Qwen3.5-9B-gguf','bnb_fp4','bfloat16'),('Qwen3.5-9B-gguf','bnb_nf4','float16')):
    cfg = {'model':model,'quantization':quant,'precision':precision,
           'kv_quantization':'hqq_8','prefix_cache':False,'max_tokens':128,
           'temperature':0,'enable_thinking':False,'tools':[TOOL],'tool_choice':'auto'}
    for label,system in (('long',SYSTEM),('short','Answer accurately from the actual image. Use tools only when needed.'),('absent','')):
        for candidate in (False,True):
            text = system + ('\n'+GUIDANCE if candidate else '')
            prefix = [{'role':'system','content':text}] if text else []
            cases = ['text','red','yellow','photo','vision_tool']
            for case in cases:
                messages = followup if case=='vision_tool_result' else prefix+[message(case)]
                prior = '\n'.join(m.get('content') or '' for m in messages if m['role']=='assistant')
                answer = request('/v1/chat/completions',{**cfg,'messages':messages})['choices'][0]['message']
                passed = correct(case,answer,prior)
                rows.append({'settings':{k:cfg[k] for k in ('model','quantization','precision')},
                    'system_label':label,'system':text,'candidate':candidate,
                    'case':case,'answer':answer,'correct':passed})
                target.write_bytes(gzip.compress(json.dumps(rows,ensure_ascii=False,indent=2).encode()))
                print(model,quant,precision,label,candidate,case,passed,flush=True)
                if case=='vision_tool' and passed:
                    followup = messages+[answer,{'role':'tool','tool_call_id':answer['tool_calls'][0]['id'],
                        'content':'{"city":"Hong Kong","temperature_c":21,"condition":"cloudy"}'}]
                    cases.append('vision_tool_result')
print({key:sum(r['correct'] for r in rows if r['candidate']==key) for key in (False,True)},flush=True)
