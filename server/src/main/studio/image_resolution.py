from ..errors import UserError


def apply(params,args):
    size=args.get('size',1024)
    if type(size) is not int or size not in (512,768,1024):
        raise UserError('Image size must be 512, 768 or 1024')
    scale=size/max(params['width'],params['height'])
    for key in ('width','height'):
        params[key]=max(64,round(params[key]*scale/64)*64)
