import time
from .ids import new
from .store import encode
from .image_store import reserve,save,metadata
from .branches import idle


def record(e,source,picture,recipe,chat=None):
    if chat:
        idle(e,chat)
        parent=e.db.get('chats',chat)['tip']
    with e.db.transaction():
        user=new() if chat else None
        message=new() if chat else None
        recipe={**recipe,'method':'pillow:'+recipe['operation']}
        ident=reserve(e.db,chat,message,recipe,[source],kind='edited')
        save(e.db,ident,picture)
        if chat:
            number=e.db.reference(chat,source)
            e.db.insert('messages',id=user,chat_id=chat,parent_id=parent,role='user',
                parts_json=encode([{'type':'text','text':f'Quick edit: {recipe["operation"]} (Image {number})'},
                                   {'type':'images','images':[source]}]),created=time.time())
            parts=[{'type':'activity','text':'Edited image: '+recipe['operation']},
                   {'type':'images','images':[ident]}]
            e.db.insert('messages',id=message,chat_id=chat,parent_id=user,role='assistant',
                        parts_json=encode(parts),created=time.time())
            e.db.update('chats',chat,tip=message,updated=time.time())
            e.events.publish(chat,'message.updated',{'message_id':message})
            e.events.publish('*','chats.changed',{'chat_id':chat})
    return metadata(e.db,ident,chat)
