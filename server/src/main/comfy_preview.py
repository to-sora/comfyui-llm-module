import json
import struct


def decode(raw, prompt):
    if len(raw) < 8:
        return None
    kind, size = struct.unpack('>II', raw[:8])
    if kind == 1:
        data = {'prompt_id':prompt, 'image_type':'image/png' if size==2 else 'image/jpeg'}
        content = raw[8:]
    elif kind == 4:
        data = json.loads(raw[8:8+size])
        data.setdefault('prompt_id', prompt)
        content = raw[8+size:]
    else:
        return None
    return {'type':'preview', 'data':{**data, 'bytes':content}}
