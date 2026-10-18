from PIL import Image
from ..generation import source_size
from ..errors import UserError


def prepare(original,mask,params):
    box=mask.getbbox()
    if not box:
        raise UserError('Paint an area before asking for a masked edit')
    x0,y0,x1,y1=box
    pad=max(96,round(max(x1-x0,y1-y0)*.3))
    box=(max(0,x0-pad),max(0,y0-pad),min(original.width,x1+pad),min(original.height,y1+pad))
    crop=original.crop(box)
    size=source_size(crop.size)
    params.update(edit_region=list(box),width=size[0],height=size[1],mask_encoding='source_latent_crop')
    return crop.resize(size,Image.Resampling.LANCZOS),mask.crop(box).resize(size,Image.Resampling.NEAREST)


def composite(picture,original,mask,params):
    box=params.get('edit_region')
    if box:
        result=original.copy()
        crop=picture.resize((box[2]-box[0],box[3]-box[1]),Image.Resampling.LANCZOS)
        result.paste(crop,box[:2])
        return Image.composite(result,original,mask)
    return Image.composite(picture.crop((0,0,*original.size)),original,mask)
