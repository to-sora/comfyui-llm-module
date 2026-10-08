from .catalog import styles
from ..generation import recipe


def field(kind, **values):
    return {'type':kind, **values}


def tool(name, description, properties, required):
    return {'type':'function','function':{'name':name,'description':description,
        'parameters':{'type':'object','properties':properties,'required':required,'additionalProperties':False}}}


def schemas(caps):
    image = field('integer', minimum=1, description='Image number shown in this chat; never invent zero-based array indexes.')
    catalog = styles(caps)
    return [
        tool('generate_images','Generate the whole requested set together. Describe each desired final image. Leave seed absent for fresh images.', {
            'images':field('array',minItems=1,maxItems=8,items=field('object',properties={
                'prompt':field('string'),'negative':field('string')},required=['prompt'],additionalProperties=False)),
            'style':field('string',enum=list(catalog),description='; '.join(k+': '+v['describe'] for k,v in catalog.items())),
            'aspect':field('string',enum=list(recipe()['aspects'])),
            'seed':field('integer',minimum=0,description='Only provide to reproduce a previous result.')}, ['images','style','aspect']),
        tool('edit_image','Change an existing image. Keep its aspect. Describe the complete desired image. Use an area only when the user supplied a mask.', {
            'image':image,'instruction':field('string'),'area':image,
            'strength':field('string',enum=['low','medium','high'],description='low .35, medium .5, high .7; default medium')}, ['image','instruction']),
        tool('upscale_image','Make an image twice as large, up to the 4096 pixel limit.',
             {'image':image,'factor':field('integer',enum=[2])},['image','factor']),
        tool('remove_background','Remove a simple, near-uniform background, retaining transparency. Complex-background model support is still pending.',
             {'image':image},['image']),
        tool('look_at_images','Look at actual pixels before evaluating images. Newly made images are attached automatically after a batch.',
             {'images':field('array',items=image,minItems=1,maxItems=8)},['images'])]
