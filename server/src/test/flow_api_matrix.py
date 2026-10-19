"""User's explicit three-message, 2/1/2-image flow; real inference, one PID."""
import gzip
import json
from pathlib import Path
from plugin.src.test.api_client import request
from .studio_helpers import OUT,record
from .flow_spec import PROFILES,SETTINGS
from .flow_api_prompt import SYSTEM
from .flow_api_round import execute
from .flow_api_catalog import detect


def run():
    pid=json.loads(Path('plugin/data/service.json').read_text())['pid']
    file=OUT/'flow-api-progress.json'
    state=json.loads(file.read_text()) if file.exists() else {'pid':pid,'settings':SETTINGS,'profiles':{}}
    assert state['pid']==pid,'Cannot resume once-read evidence after ComfyUI restart'
    caps=detect()
    for profile in PROFILES:
        p=state['profiles'].setdefault(profile,{'completed':0,'seconds':0,'images':0,'pair':[]})
        if p['completed']==25:continue
        transcript=OUT/f'flow-api-{profile}-messages.json.gz'
        messages=json.loads(gzip.decompress(transcript.read_bytes())) if transcript.exists() else [
            {'role':'system','content':SYSTEM}]
        for index in range(p['completed']+1,26):
            result=execute(profile,index,p['pair'],pid,caps,messages)
            p.update(completed=index,pair=result['pair'])
            p['seconds']+=result['seconds'];p['images']+=5
            samples=result['observation']['host']
            minimum=min(s['planned_available'] for s in samples)
            p['min_planned_available']=min(p.get('min_planned_available',minimum),minimum)
            p['peak_rss']=max(p.get('peak_rss',0),max(s['comfy_rss'] for s in samples))
            transcript.write_bytes(gzip.compress(json.dumps(messages).encode()))
            record('flow-api-progress',state)
    print('PASS: four profiles, 100 rounds, 300 LLM calls, 500 images (+4 sharing probes)',flush=True)


if __name__=='__main__':run()
