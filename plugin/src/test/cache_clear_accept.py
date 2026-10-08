import json
import time
from pathlib import Path
from .api_client import request

body = {"model":"Qwen3.5-9B", "max_tokens":16,
        "messages":[{"role":"user","content":"What is 17 + 25? Reply with only the number."}]}
assert request('/v1/chat/completions', body)['choices'][0]['message']['content'].strip() == '42'
before = request('/llm/status')
assert before['models']
request('/free', {'unload_models':True,'free_memory':True}, binary=True)
for _ in range(80):
    cleared = request('/llm/status')
    if not cleared['models']:
        break
    time.sleep(.25)
else:
    raise AssertionError('ComfyUI cleared its caches but an LLM runtime remains strongly retained')
assert request('/v1/chat/completions', body)['choices'][0]['message']['content'].strip() == '42'
after = request('/llm/status')
assert len(after['models']) == 1
evidence = {'status':'PASS','comfy_clear_releases_all_handles':True,
    'models_before':len(before['models']),'models_after_clear':len(cleared['models']),
    'models_after_reload':len(after['models']),'answer_after_reload':'42',
    'cuda_allocated':[s['cuda_allocated'] for s in (before,cleared,after)]}
dest = Path(__file__).resolve().parents[3]/'fan-out/studio-engine/cache-clear.json'
dest.write_text(json.dumps(evidence,indent=2))
print(evidence)
