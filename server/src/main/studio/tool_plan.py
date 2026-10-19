import json
import secrets
from .catalog import image_settings, styles
from .image_store import reserve, number
from ..errors import UserError
from ..generation import seed, recipe
from .tool_arguments import edit_defaults,images_argument,description,mask_for
from .image_assistant import actual


def plan(e, run, calls):
    tasks, results = [], {}
    for call in calls:
        function = call['function']
        name, args = function['name'], json.loads(function['arguments'])
        if not isinstance(args,dict):
            raise UserError('Tool arguments must be an object')
        output = []
        if name=='generate_images':
            images = images_argument(args.get('images'))
            from .generation_plan import parameters
            for item in images:
                p = parameters(e.caps,args,item)
                output.append(add(e,run,tasks,p,call['id']))
        elif name in ('edit_image','upscale_image','remove_background'):
            source = number(e.db,run['chat_id'],args.get('image'))
            p = {**edit_defaults(e,source,name=='edit_image' and args.get('operation','sdxl')=='sdxl'),'source':source['id'],
                 'operation':name,'seed':secrets.randbits(52)}
            if name=='edit_image':
                from .edit_plan import configure
                configure(e,run,source,p,args)
                checkpoint(e,p,args)
            elif name=='upscale_image' and args.get('factor')!=2:
                raise UserError('Upscale supports factor 2')
            output.append(add(e,run,tasks,p,call['id'],[source['id']]))
        elif name=='look_at_images':
            output=[number(e.db,run['chat_id'],i)['id'] for i in images_argument(args.get('images'))]
        else:
            raise UserError('The assistant requested an unknown tool')
        results[call['id']]=output
    return tasks,results


def checkpoint(e,p,args):
    if 'checkpoint' in args:
        if args['checkpoint'] not in e.caps['checkpoints']:
            raise UserError('Choose an available SDXL checkpoint')
        p['checkpoint']=args['checkpoint']


def add(e,run,tasks,p,call,parents=None):
    if run['settings'].get('image_checkpoint'):
        p['checkpoint']=run['settings']['image_checkpoint']
    p['assistant']=actual(e,run)
    ident=reserve(e.db,run['chat_id'],run['assistant_id'],p,parents)
    tasks.append({'id':ident,'params':p,'call':call})
    return ident
