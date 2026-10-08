import time
import uuid
from urllib.parse import urlencode
from ..main.comfy import Comfy
from ..main.assets import png, decode
from ..main.prompt_cleanup import cleanup
from ..main.studio.workflows import build
from ..main.graph import node


async def generate(params, source, mask, grow=0, preserve=False):
    comfy = Comfy()
    await comfy.start()
    ident = str(uuid.uuid4())
    future, completed = None, False
    started = time.monotonic()
    try:
        image = await comfy.upload(png(source),ident+'.png')
        area = await comfy.upload(png(mask),ident+'-mask.png')
        graph = build({**params,'output_key':ident},[params['seed']],image,area)
        if preserve:
            graph['14'] = node('VAEEncode',pixels=['12',0],vae=['1',2])
            graph['4'] = node('SetLatentNoiseMask',samples=['14',0],mask=['13',0])
        else:
            graph.pop('14',None)
            graph['4'] = node('VAEEncodeForInpaint',pixels=['12',0],vae=['1',2],
                              mask=['13',0],grow_mask_by=grow)
        async def event(value):
            pass
        future = await comfy.events.subscribe(ident,event)
        await comfy.request('/prompt',{'prompt':graph,'prompt_id':ident,
                            'client_id':comfy.events.client_id})
        value = await comfy.history(ident,future)
        completed = True
        remote = value['outputs']['11']['images'][0]
        raw = await comfy.request('/view?'+urlencode(remote),binary=True)
        return decode(raw),{'prompt':ident,'seconds':time.monotonic()-started,'graph':graph}
    finally:
        await cleanup(comfy,ident,completed,future)
        await comfy.close()
