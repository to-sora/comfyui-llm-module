import base64
import io
from pathlib import Path
from PIL import Image
from .model_cases import image_message


def message(case):
    if case!='photo':
        return image_message(case)
    path = Path(__file__).resolve().parents[3]/'fan-out/studio-chat/engine-recheck-image.png'
    picture = Image.open(path).convert('RGB')
    picture.thumbnail((512,512))
    buffer = io.BytesIO()
    picture.save(buffer,format='JPEG')
    url = 'data:image/jpeg;base64,'+base64.b64encode(buffer.getvalue()).decode()
    return {'role':'user','content':[
        {'type':'text','text':'What is the main object in this picture? Reply with one short noun phrase.'},
        {'type':'image_url','image_url':{'url':url}}]}
