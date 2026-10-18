from .basic_edits import OPERATIONS
from .tool_arguments import mask_for
from ..errors import UserError
from ..generation import recipe


def configure(e,run,source,p,args):
    instruction=args.get('instruction')
    if not isinstance(instruction,str) or not instruction.strip():
        raise UserError('Describe what should change')
    operation=args.get('operation','sdxl')
    if operation=='sdxl':
        p.update(prompt=instruction,negative='',denoise=recipe()['strengths'].get(args.get('strength','medium')))
        if p['denoise'] is None:
            raise UserError('Choose low, medium or high edit strength')
    elif operation in OPERATIONS:
        options=args.get('options',{})
        if not isinstance(options,dict):
            raise UserError('Local edit options must be an object')
        p.update(operation=operation,edit_options={**options,'operation':operation},
                 instruction=instruction,method='pillow:'+operation)
    else:
        raise UserError('Choose an available image edit operation')
    if args.get('area') is not None:
        p['mask']=mask_for(e,run['chat_id'],source,args['area'])
