import io
from PIL import Image,ImageDraw
from ..settings import DATA


def vision(db,ident,chat):
    from .image_store import metadata,load
    metadata(db,ident,chat)
    cache=DATA/'vision'/(ident+'-alpha.jpg')
    cache.parent.mkdir(exist_ok=True)
    if cache.is_file():
        return cache.read_bytes()
    picture=load(db,ident,chat)
    picture.thumbnail((512,512),Image.Resampling.LANCZOS)
    canvas=Image.new('RGB',picture.size,'#eeeeee')
    draw=ImageDraw.Draw(canvas)
    for y in range(0,picture.height,16):
        for x in range(0,picture.width,16):
            if (x//16+y//16)%2:
                draw.rectangle((x,y,x+15,y+15),fill='#bcbcbc')
    canvas.paste(picture,mask=picture.getchannel('A'))
    stream=io.BytesIO()
    canvas.save(stream,format='JPEG',quality=85)
    raw=stream.getvalue()
    cache.write_bytes(raw)
    return raw
