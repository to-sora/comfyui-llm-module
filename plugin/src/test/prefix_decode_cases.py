import base64
import io
import json
import re
from pathlib import Path
from PIL import Image
from .model_cases import image_message


def message(case):
    if case in ('text', 'tool'):
        text = 'What is 17 + 25? Reply with only the number.' if case == 'text' else 'What is the weather in Hong Kong?'
        return {'role':'user', 'content':text}
    if case == 'vision_tool':
        result = image_message('blue')
        result['content'][0]['text'] = 'Name the image color, then use the weather tool for Hong Kong.'
        return result
    if case == 'multi':
        result = image_message('blue')
        result['content'][0]['text'] = 'Name the two image colors in order. Only the two color names.'
        result['content'].append(image_message('yellow')['content'][1])
        return result
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


def correct(case, value, prior=''):
    content = (value.get('content') or '').lower()
    calls = value.get('tools', [c['function'] for c in value.get('tool_calls', [])])
    if case in ('tool', 'vision_tool'):
        return (len(calls) == 1 and calls[0]['name'] == 'get_weather' and
                json.loads(calls[0]['arguments']).get('city', '').lower() == 'hong kong')
    if calls:
        return False
    if case == 'vision_tool_result':
        return 'blue' in (prior.lower()+content) and '21' in content and 'cloudy' in content
    if case == 'photo':
        return any(w in content for w in ('cup', 'mug'))
    if case == 'text':
        return content.strip() == '42'
    if case == 'multi':
        return re.findall('blue|yellow', content) == ['blue', 'yellow']
    return content.strip(' .!\n') == case
