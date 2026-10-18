from PIL import Image,ImageDraw,ImageFont,ImageChops,ImageOps
from ..assets import check_size
from ..errors import UserError
from ..settings import APP


def apply(image,p):
    op=p['operation']
    result=image.copy()
    color=p.get('color','#ffffff')
    if op=='text':
        text=p.get('text','')
        if not isinstance(text,str) or not 1<=len(text)<=2000:
            raise UserError('Enter between 1 and 2,000 characters')
        size=max(8,min(512,int(p.get('size',48))))
        fonts=list((APP/'data/fonts').glob('*.ttc'))+list((APP/'data/fonts').glob('*.ttf'))+list((APP/'data/fonts').glob('*.otf'))
        font=ImageFont.truetype(str(fonts[0]),size) if fonts else ImageFont.load_default(size=size)
        ImageDraw.Draw(result).multiline_text((int(p.get('x',20)),int(p.get('y',20))),text,
                                             font=font,fill=color,stroke_width=max(0,min(20,int(p.get('stroke',0)))))
    elif op=='border':
        amount=max(1,min(512,int(p.get('amount',24))))
        check_size((image.width+2*amount,image.height+2*amount))
        result=ImageOps.expand(image,border=amount,fill=color)
    elif op=='opacity':
        factor=max(0,min(1,float(p.get('amount',.5))))
        result.putalpha(image.getchannel('A').point(lambda n:round(n*factor)))
    elif op=='rounded_corners':
        mask=Image.new('L',image.size)
        ImageDraw.Draw(mask).rounded_rectangle((0,0,image.width-1,image.height-1),
            radius=max(0,min(min(image.size)//2,int(p.get('amount',48)))),fill=255)
        result.putalpha(ImageChops.multiply(mask,image.getchannel('A')))
    elif op=='canvas':
        size=(int(p.get('width',image.width)),int(p.get('height',image.height)))
        check_size(size)
        result=Image.new('RGBA',size,color)
        result.alpha_composite(image,((size[0]-image.width)//2,(size[1]-image.height)//2))
    return result
