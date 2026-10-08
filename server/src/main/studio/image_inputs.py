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
    mask = load(e.db,p['mask'],run['chat_id']).convert('L') if p.get('mask') else None
    if mask is not None:
        if mask.size != original.size:
            raise UserError('The painted area must match the original image size')
        p['mask_encoding'] = 'source_latent'
        p['width'],p['height'] = ((n+7)//8*8 for n in original.size)
        padded = Image.new('RGBA',(p['width'],p['height']))
        padded.paste(original,(0,0))
        padded_mask = Image.new('L',padded.size)
        padded_mask.paste(mask,(0,0))
        mask_name = await e.comfy.upload(png(padded_mask),key+'-mask.png')
    else:
        p['width'],p['height'] = source_size(original.size)
        padded = ImageOps.pad(original,(p['width'],p['height']),Image.Resampling.LANCZOS)
        mask_name = None
    source = await e.comfy.upload(png(padded),key+'.png')
    return source,mask_name,original,mask
