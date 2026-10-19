from urllib.parse import urlencode
from plugin.src.test.api_client import API
from server.src.main.studio.generation_plan import parameters
from server.src.main.studio.workflows import build
from .flow_api_io import image


def generate(caps,args,token,stage,observer,start=1):
    results=[]
    for number,item in enumerate(args['images'],start):
        p=parameters(caps,args,item)
        assert (p['width'],p['height'])==(512,512),p
        p['output_key']=f'{token}-{stage}-{number}'
        graph=build(p,[p['seed']])
        graph['1']['inputs']['lease']=token
        result=image(graph,observer)
        file=result['outputs']['11']['images'][0]
        results.append({'image':number,'url':API+'/view?'+urlencode(file),
                        'prompt':item['prompt'],'checkpoint':p['checkpoint'],
                        'settings':p,'job':result})
    return results
