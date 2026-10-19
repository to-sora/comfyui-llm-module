from .catalog import styles
from ..generation import recipe


def field(kind, **values):
    return {'type':kind, **values}


def tool(name, description, properties, required):
    return {'type':'function','function':{'name':name,'description':description,
        'parameters':{'type':'object','properties':properties,'required':required,'additionalProperties':False}}}


def schemas(caps):
    from .edit_schema import fields
    from .image_tool_schema import fields as image_fields
    image = field('integer', minimum=1, description='Image number shown in this chat; never invent zero-based array indexes.')
    catalog = styles(caps)
    return [
        tool('generate_images','Generate an independent batch together. Leave seed absent for fresh images.',
             image_fields(caps,field), ['images']),
        tool('edit_image','Change an existing image. Keep its aspect. Describe the complete desired image. Use an area only when the user supplied a mask.', {
            'image':image,'instruction':field('string'),'area':image,**fields(),
            'checkpoint':field('string',enum=caps['checkpoints']),
            'strength':field('string',enum=['low','medium','high'],description='low .35, medium .5, high .7; default medium')}, ['image','instruction']),
        tool('upscale_image','Make an image twice as large, up to the 4096 pixel limit.',
             {'image':image,'factor':field('integer',enum=[2])},['image','factor']),
        tool('remove_background','Remove the background with a local foreground segmentation model, retaining transparency.',
             {'image':image},['image']),
        tool('look_at_images','Look at actual pixels before evaluating images. Newly made images are attached automatically after a batch.',
             {'images':field('array',items=image,minItems=1,maxItems=8)},['images'])]
