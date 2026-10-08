import gzip
import json
import sys
from studio_helpers import ROOT,OUT,record
sys.path.insert(0,str(ROOT))
from plugin.src.test.api_client import request
from server.src.main.studio.agent_tools import prepare,repair
from server.src.main.errors import UserError

# Replay the actual request that produced a duplicate batch in Firefox UAT.
captured=json.loads(gzip.decompress((OUT/'retry-duplicate-before-fix.json.gz').read_bytes()))
steps=captured['trace']['steps']
body=dict(next(s['body'] for s in steps if s['kind']=='request'))
body.update(stream=False)
body.pop('comfy_prompt_id',None)
first=request('/v1/chat/completions',body)['choices'][0]['message']
try:
    prepare(None,None,first['tool_calls'])
except UserError as error:
    assert 'Repeated identical' in str(error),str(error)
    correction=repair(first,error)
else:
    raise AssertionError('The captured model failure was not reproduced')
second=request('/v1/chat/completions',{**body,'messages':body['messages']+[first]+correction})['choices'][0]['message']
calls=second.get('tool_calls',[])
assert len(calls)==1 and calls[0]['function']['name']=='generate_images',second
args=json.loads(calls[0]['function']['arguments'])
assert len(args['images'])==4,args
record('duplicate-repair',{'status':'PASS','actual_captured_request':True,
    'duplicate_calls':len(first['tool_calls']),'repaired_calls':len(calls),'repaired_images':4,
    'rejected_before_database_or_gpu_image_work':True})
record('duplicate-repair-models',{'before':first,'repair':correction,'after':second})
print('Actual duplicate model output rejected; one real repair returns four images in one call PASS')
