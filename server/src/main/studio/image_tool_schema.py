from .catalog import styles
from ..generation import recipe


def fields(caps,field):
    catalog=styles(caps)
    style=field('string',enum=list(catalog))
    aspect=field('string',enum=list(recipe()['aspects']))
    size=field('integer',enum=[512,768,1024],description='Longest edge in pixels; default 1024.')
    return {'images':field('array',minItems=1,maxItems=8,items=field('object',properties={
        'prompt':field('string'),'negative':field('string'),
        'checkpoint':field('string',enum=caps.get('batch_checkpoints',caps['checkpoints']),
                           description='Available models that fit a retained pair.'),
        'style':style,'aspect':aspect,'size':size},required=['prompt'],additionalProperties=False)),
        'style':field('string',enum=list(catalog),description='; '.join(k+': '+v['describe'] for k,v in catalog.items())),
        'checkpoint':field('string',enum=caps.get('batch_checkpoints',caps['checkpoints']),
                           description='Default model for images without their own checkpoint.'),
        'aspect':aspect,'size':size,'seed':field('integer',minimum=0,
                                               description='Only set to reproduce an image.')}
