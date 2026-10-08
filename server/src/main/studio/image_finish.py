import asyncio
from urllib.parse import urlencode
from PIL import Image
from .image_store import save, metadata
from .store import encode
from ..assets import decode


async def finish(e,run,tasks,prompt,outputs,original,mask):
    images=outputs['11']['images']
    if len(images)!=len(tasks):
        raise RuntimeError('The image engine returned a different number of results than requested')
    seeds=[t['params']['seed'] for t in tasks]
    for index,(task,remote) in enumerate(zip(tasks,images)):
        raw=await e.comfy.request('/view?'+urlencode(remote),binary=True)
        picture=await asyncio.to_thread(decode,raw)
        if mask is not None:
            picture=Image.composite(picture.crop((0,0,*original.size)),original,mask)
            raw=None
        recipe={**task['params'],'batch_seeds':seeds,'batch_index':index,'prompt_id':prompt}
        save(e.db,task['id'],picture,raw,recipe_json=encode(recipe))
        e.previews.pop(task['id'],None)
        e.publish(run,'image.done',{'image':metadata(e.db,task['id'],run['chat_id'])})
