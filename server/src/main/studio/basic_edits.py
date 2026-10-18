from PIL import Image,ImageOps,ImageEnhance,ImageFilter
from ..errors import UserError
from ..assets import check_size

OPERATIONS=['resize','crop','rotate','flip_horizontal','flip_vertical','brightness','contrast',
            'saturation','sharpness','blur','grayscale','sepia','invert','autocontrast','equalize',
            'text','border','opacity','rounded_corners','canvas']


def apply(image,p):
    op=p.get('operation')
    if op not in OPERATIONS:
        raise UserError('Choose an available edit')
    if op=='resize':
        size=(int(p.get('width',image.width)),int(p.get('height',image.height)))
        check_size(size)
        return image.resize(size,Image.Resampling.LANCZOS)
    if op=='crop':
        box=tuple(int(p.get(k,v)) for k,v in zip(('left','top','right','bottom'),(0,0,*image.size)))
        if not 0<=box[0]<box[2]<=image.width or not 0<=box[1]<box[3]<=image.height:
            raise UserError('Crop must be inside the source image')
        return image.crop(box)
    if op=='rotate':
        angle=int(p.get('angle',90))
        if angle not in (90,180,270):
            raise UserError('Choose 90, 180 or 270 degrees')
        return image.rotate(angle,expand=True)
    if op.startswith('flip_'):
        return (ImageOps.mirror if op=='flip_horizontal' else ImageOps.flip)(image)
    if op in ('brightness','contrast','saturation','sharpness'):
        cls={'brightness':ImageEnhance.Brightness,'contrast':ImageEnhance.Contrast,
             'saturation':ImageEnhance.Color,'sharpness':ImageEnhance.Sharpness}[op]
        return cls(image).enhance(max(0,min(4,float(p.get('amount',1.2)))))
    if op=='blur':
        return image.filter(ImageFilter.GaussianBlur(max(0,min(100,float(p.get('amount',2))))))
    if op in ('grayscale','sepia','invert','autocontrast','equalize'):
        rgb=image.convert('RGB')
        if op=='grayscale':
            result=ImageOps.grayscale(rgb).convert('RGB')
        elif op=='sepia':
            result=ImageOps.colorize(ImageOps.grayscale(rgb),'#241208','#f6dfb4')
        else:
            result=getattr(ImageOps,op)(rgb)
        result.putalpha(image.getchannel('A'))
        return result
    from .decorative_edits import apply as decorate
    return decorate(image,p)
