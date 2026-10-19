import secrets
from .catalog import image_settings,styles
from .tool_arguments import description
from .image_resolution import apply
from ..generation import seed
from ..errors import UserError


def parameters(caps,args,item):
    description(item)
    style=item.get('style',args.get('style','photo'))
    aspect=item.get('aspect',args.get('aspect','square'))
    value=image_settings(caps,style,aspect)
    apply(value,{**args,**item})
    name=item.get('checkpoint',args.get('checkpoint',value['checkpoint']))
    if name not in caps['checkpoints']:
        raise UserError('Choose an available SDXL checkpoint')
    value.update(checkpoint=name,prompt=item['prompt'],negative=item.get('negative',''),
                 seed=seed(args['seed']) if 'seed' in args else secrets.randbits(52))
    value['requested_prompt']=value['prompt']
    value['prompt']+=', '+styles(caps)[style]['prompt_suffix']
    return value
