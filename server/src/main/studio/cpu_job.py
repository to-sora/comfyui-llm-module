import asyncio
from PIL import Image
from .image_store import load, save, metadata
from .store import encode
from ..edit_color import apply
from ..errors import UserError


def edit(picture,p):
    if p['operation']=='upscale_image':
        scale=min(2,4096/max(picture.size))
        if scale<=1:
            raise UserError('This image is already at the 4096 pixel limit')
        return picture.resize(tuple(round(n*scale) for n in picture.size),Image.Resampling.LANCZOS)
    return apply(picture,'remove_background',{'color':'','tolerance':24,'softness':16})


async def execute(e,run,task):
    e.check(run)
    e.publish(run,'image.progress',{'image_id':task['id'],'message':'Editing the image'})
    source=load(e.db,task['params']['source'],run['chat_id'])
    picture=await asyncio.to_thread(edit,source,task['params'])
    recipe={**task['params'],'method':'lanczos' if task['params']['operation']=='upscale_image' else 'border_color'}
    save(e.db,task['id'],picture,recipe_json=encode(recipe))
    e.publish(run,'image.done',{'image':metadata(e.db,task['id'],run['chat_id'])})
