import copy
from urllib.parse import urlencode
from .image_store import metadata, vision


async def attach(e, chat, ids, text):
    parts = [{'type':'text','text':text}]
    sources={p for ident in ids for p in metadata(e.db,ident,chat)['parents']
             if metadata(e.db,ident,chat)['kind']=='mask'}
    for ident in dict.fromkeys(ids):
        item = metadata(e.db,ident,chat)
        filename = 'studio-vision-'+ident+'.jpg'
        await e.comfy.upload(vision(e.db,ident,chat),filename)
        url = e.comfy.url+'/view?'+urlencode({'filename':filename,'type':'input'})
        label=f'Image {item["number"]}'
        if ident in sources:
            label+=' — selected source image to edit'
        if item['kind']=='mask' and item['parents']:
            source=metadata(e.db,item['parents'][0],chat)
            label+=f' — painted mask for source image {source["number"]}; only white areas can change'
        parts.extend([{'type':'text','text':label},
                      {'type':'image_url','image_url':{'url':url}}])
    return {'role':'user','content':parts if ids else text}


def compact(messages):
    result = copy.deepcopy(messages)
    for message in result:
        if isinstance(message.get('content'),list):
            message['content'] = '\n'.join(p.get('text','[Image pixels shown in this turn]')
                                           for p in message['content'])
        for field in ('chat','id','images'):
            message.pop(field,None)
    return result
