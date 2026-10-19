from ..errors import UserError


def settings(caps, requested=None):
    value = {'model':'Qwen3.5-9B','quantization':'default','kv_quantization':'hqq_8',
             'context_tokens':16384,'max_tokens':1024,'precision':'bfloat16',
             'image_checkpoint':'','enable_thinking':False,'max_image_tokens':16000,
             'parallel_tool_calls':True}
    value.update({k:v for k,v in (requested or {}).items() if k in value})
    for key in ('model','quantization','kv_quantization','precision','image_checkpoint'):
        if not isinstance(value[key],str):
            raise UserError('Model and quantization choices must be text')
    if value['model']=='gemma-4-E2B':
        value['model']='gemma-3-12b-it'
    if not value['model'].strip() or len(value['model'])>400:
        raise UserError('Enter a model profile, local path or Hugging Face repository')
    if value['precision'] not in ('bfloat16','float16'):
        raise UserError('Select a supported model precision')
    if value['image_checkpoint'] and caps and value['image_checkpoint'] not in caps['checkpoints']:
        raise UserError('Select an available SDXL checkpoint')
    if value['kv_quantization'] not in ('none','hqq_4','hqq_8'):
        raise UserError('Select a supported KV quantization')
    if value['quantization'] not in ('default','auto','none','bnb_nf4','bnb_fp4','bnb_int8'):
        raise UserError('Select a supported weight quantization')
    for key in ('context_tokens','max_tokens','max_image_tokens'):
        if type(value[key]) is not int:
            raise UserError(f'{key} must be an integer')
    if any(type(value[k]) is not bool for k in ('enable_thinking','parallel_tool_calls')):
        raise UserError('Thinking and parallel tools must be enabled or disabled')
    if not 64<=value['max_image_tokens']<=16384:
        raise UserError('Image tokens must be between 64 and 16384 per image')
    if not 128<=value['context_tokens']<=262144 or not 1<=value['max_tokens']<=min(32768,value['context_tokens']-1):
        raise UserError('Reply length must fit in the assistant context')
    return value
