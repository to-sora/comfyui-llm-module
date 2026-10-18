from ..errors import UserError
from . import chat_store
from .catalog import settings
from .image_store import metadata
from .message_api_data import preferences
from .run_worker import notify


def enqueue(e,chat,text,images,parent=...,documents=None):
    if not isinstance(text,str) or len(text)>100000:
        raise UserError('Use a message of at most 100,000 characters')
    if not isinstance(images,list) or len(images)>8 or any(not isinstance(i,str) for i in images):
        raise UserError('Attach up to eight images')
    from .documents import get
    documents=documents or []
    if not isinstance(documents,list) or len(documents)>8:
        raise UserError('Attach up to eight documents')
    for ident in documents:
        get(e.db,ident)
    if not text.strip() and not images and not documents:
        raise UserError('Write a message or attach a picture')
    for ident in images:
        if not metadata(e.db,ident)['file']:
            raise UserError('Wait for the attached image to finish')
    if e.db.one("SELECT id FROM runs WHERE chat_id=? AND status IN ('queued','running')",(chat,)):
        raise UserError('Wait for this chat’s reply, or stop it first')
    config={**preferences(e).get('assistant',{}),**e.db.get('chats',chat)['settings']}
    if parent is not ... and parent is not None and e.db.get('messages',parent)['chat_id']!=chat:
        raise UserError('Choose a message from this chat')
    value=chat_store.turn(e.db,chat,text,images,settings(e.caps,config),parent,documents)
    e.events.publish(chat,'message.updated',value)
    e.events.publish('*','chats.changed',{'chat_id':chat})
    notify(e)
    e.wake.set()
    return value

