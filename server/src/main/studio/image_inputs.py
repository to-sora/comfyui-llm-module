from PIL import Image, ImageOps
from .image_store import load
from ..assets import png
from ..generation import source_size
from ..errors import UserError


async def prepare(e, run, task, key):
    p = task['params']
    if not p.get('source'):
        return None,None,None,None
    original = load(e.db,p['source'],run['chat_id'])
    if p.get('operation')=='remove_background':
        p['width'],p['height']=original.size
        p['method']='u2netp'
        return await e.comfy.upload(png(original),key+'.png'),None,original,None
    mask = load(e.db,p['mask'],run['chat_id']).convert('L') if p.get('mask') else None
    if mask is not None:
        if mask.size != original.size:
            raise UserError('The painted area must match the original image size')
        from .edit_region import prepare as region
        padded,padded_mask=region(original,mask,p)
        mask_name = await e.comfy.upload(png(padded_mask),key+'-mask.png')
    else:
        p['width'],p['height'] = source_size(original.size)
        padded = ImageOps.pad(original,(p['width'],p['height']),Image.Resampling.LANCZOS)
        mask_name = None
    source = await e.comfy.upload(png(padded),key+'.png')
    return source,mask_name,original,mask
