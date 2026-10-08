import yaml
from ..settings import APP
from ..generation import recipe
from ..errors import UserError


def styles(caps):
    configured = yaml.safe_load((APP/'config/content-config/styles.yaml').read_text())
    return {key: value for key, value in configured.items() if value['checkpoint'] in caps['checkpoints']}


def settings(caps, requested=None):
    value = {'model':'Qwen3.5-9B','quantization':'default','kv_quantization':'hqq_8',
             'context_tokens':16384,'max_tokens':1024,'precision':'bfloat16','image_checkpoint':''}
    value.update({k:v for k,v in (requested or {}).items() if k in value})
    if any(not isinstance(value[k],str) for k in ('model','quantization','kv_quantization','precision','image_checkpoint')):
        raise UserError('Model and quantization choices must be text')
    if value['model']=='gemma-4-E2B':
        value['model']='gemma-3-12b-it'
    if caps and value['model'] not in {p['id'] for p in caps['profiles']}:
        raise UserError('Select an available assistant model')
    if value['precision'] not in ('bfloat16','float16','float32'):
        raise UserError('Select a supported model precision')
    if value['image_checkpoint'] and caps and value['image_checkpoint'] not in caps['checkpoints']:
        raise UserError('Select an available SDXL checkpoint')
    if value['kv_quantization'] not in ('none','hqq_4','hqq_8'):
        raise UserError('Select a supported KV quantization')
    if value['quantization'] not in ('default','auto','none','bnb_nf4','bnb_fp4','bnb_int8'):
        raise UserError('Select a supported weight quantization')
    for key in ('context_tokens','max_tokens'):
        if type(value[key]) is not int:
            raise UserError(f'{key} must be an integer')
    if not 128 <= value['context_tokens'] <= 262144 or not 1 <= value['max_tokens'] < value['context_tokens']:
        raise UserError('Reply length must fit in the assistant context')
    return value


def image_settings(caps, style, aspect):
    catalog = styles(caps)
    if style not in catalog or aspect not in recipe()['aspects']:
        raise UserError('Select a listed style and aspect')
    item = catalog[style]
    width,height = recipe()['aspects'][aspect]
    return {'style':style,'style_label':item['label'],'checkpoint':item['checkpoint'],
            'width':width,'height':height,'steps':28,'cfg':5.5,
            'sampler_name':'dpmpp_2m','scheduler':'karras','denoise':1.0}
