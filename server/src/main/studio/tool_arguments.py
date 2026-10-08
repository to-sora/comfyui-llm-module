from ..errors import UserError
from .catalog import image_settings
from .image_store import number,metadata


def edit_defaults(e,source):
    previous=source['recipe']
    p=image_settings(e.caps,previous.get('style','photo'),'square')
    for key in ('checkpoint','style','style_label','steps','cfg','sampler_name','scheduler'):
        if key in previous:
            p[key]=previous[key]
    if p['checkpoint'] not in e.caps['checkpoints']:
        raise UserError('The image’s original model is unavailable. Restore it before editing.')
    return p


def images_argument(value):
    if not isinstance(value,list) or not 1<=len(value)<=8:
        raise UserError('Request between one and eight images')
    return value


def description(item):
    if not isinstance(item,dict) or not isinstance(item.get('prompt'),str) or not item['prompt'].strip():
        raise UserError('Each image needs a description')
    if not isinstance(item.get('negative',''),str):
        raise UserError('An image’s negative description must be text')


def mask_for(e,chat,source,value):
    mask=number(e.db,chat,value)
    if mask['parents'] and source['id'] not in mask['parents']:
        target=metadata(e.db,mask['parents'][0],chat)
        raise UserError(f'Mask image {value} belongs to source image {target["number"]}. Use that source image.')
    if mask['file'] and source['file'] and (mask['width'],mask['height'])!=(source['width'],source['height']):
        raise UserError('The painted mask does not match the source image size')
    return mask['id']
