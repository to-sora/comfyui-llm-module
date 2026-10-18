import asyncio
from PIL import Image
from .image_store import load, save, metadata
from .store import encode
from ..errors import UserError
from ..host_guard import JOBS,admit
from .basic_edits import OPERATIONS,apply


def edit(picture,p):
    if p['operation'] in OPERATIONS:
        return apply(picture,p['edit_options'])
    if p['operation']=='upscale_image':
        scale=min(2,4096/max(picture.size))
        if scale<=1:
            raise UserError('This image is already at the 4096 pixel limit')
        return picture.resize(tuple(round(n*scale) for n in picture.size),Image.Resampling.LANCZOS)
    raise UserError('This edit must run through the image engine')


async def execute(e,run,task):
    async with JOBS:
        admit()
        await work(e,run,task)


async def work(e,run,task):
    e.check(run)
    e.publish(run,'image.progress',{'image_id':task['id'],'message':'Editing the image'})
    source=load(e.db,task['params']['source'],run['chat_id'])
    picture=await asyncio.to_thread(edit,source,task['params'])
    e.check(run)
    if task['params'].get('mask'):
        if source.size!=picture.size:
            raise UserError('A masked local edit must keep the image dimensions')
        mask=load(e.db,task['params']['mask'],run['chat_id']).convert('L')
        picture=Image.composite(picture,source,mask)
    recipe={**task['params'],'method':task['params'].get('method','lanczos')}
    save(e.db,task['id'],picture,recipe_json=encode(recipe))
    e.publish(run,'image.done',{'image':metadata(e.db,task['id'],run['chat_id'])})
