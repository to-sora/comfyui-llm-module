import gzip
import json
import statistics
import sys
from pathlib import Path
from .api_client import request

root = Path(__file__).resolve().parents[3]/'fan-out'
fixture = json.loads(gzip.decompress((root/'studio-chat/engine-recheck.json.gz').read_bytes()))
original = [s['body'] for s in fixture['run']['trace']['steps'] if s['kind']=='request'][-1]
model = sys.argv[1] if len(sys.argv)>1 else 'Qwen3.5-9B-gguf'
mode = sys.argv[2] if len(sys.argv)>2 else 'mlp_down_fp32'
body = {**original,'model':model,'quantization':'bnb_nf4','kv_quantization':'hqq_8',
        'prefix_cache':False,
        'max_tokens':64,'temperature':0,'enable_thinking':False,'stream':False}
body.pop('max_completion_tokens',None)
rows = []
target = root/f'studio-engine/prefix-benchmark-{model}-{mode}.json.gz'
for iteration in range(6):
    sample = {'iteration':iteration,'warmup':iteration==0}
    for name in (('default',mode) if iteration%2==0 else (mode,'default')):
        response = request('/v1/chat/completions',{**body,'diagnostic_prefix':name})
        status = request('/llm/status')
        profile = next(p for p in status['models'] if p['model']==model and p['kv_quantization']=='hqq_8')
        decode = profile['diagnostics']['prefix_probe']['decode']
        sample[name] = decode
        assert all(len(r['tokens'])==64 and not r['tools'] and
                   any(w in r['content'].lower() for w in ('cup','mug')) for r in decode['runs']),decode
    rows.append(sample)
    target.write_bytes(gzip.compress(json.dumps(rows,ensure_ascii=False,indent=2).encode()))
    print(iteration,round(sample['default']['runs'][0]['seconds'],3),
          round(sample[mode]['runs'][-1]['seconds'],3),flush=True)
baseline = statistics.median(r['default']['runs'][0]['seconds'] for r in rows[1:])
cached = statistics.median(r[mode]['runs'][-1]['seconds'] for r in rows[1:])
print({'baseline_median_seconds':baseline,'cached_median_seconds':cached,
       'speedup_percent':100*(baseline-cached)/baseline,'five_warm_samples':True},flush=True)
