import yaml
from ..settings import APP
from ..generation import recipe
from ..errors import UserError
from .assistant_settings import settings


def styles(caps):
    configured = yaml.safe_load((APP/'config/content-config/styles.yaml').read_text())
    return {key: value for key, value in configured.items() if value['checkpoint'] in caps['checkpoints']}


def image_settings(caps, style, aspect):
    catalog = styles(caps)
    if style not in catalog or aspect not in recipe()['aspects']:
        raise UserError('Select a listed style and aspect')
    item = catalog[style]
    width,height = recipe()['aspects'][aspect]
    return {'style':style,'style_label':item['label'],'checkpoint':item['checkpoint'],
            'width':width,'height':height,'steps':28,'cfg':5.5,
            'sampler_name':'dpmpp_2m','scheduler':'karras','denoise':1.0}
