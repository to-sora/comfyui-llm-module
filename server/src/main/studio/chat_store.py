import time
from .ids import new
from .store import encode


def create(db, title='New chat', settings=None):
    ident, now = new(), time.time()
    db.insert('chats', id=ident, title=title[:100], created=now, updated=now,
              settings_json=encode(settings or {}))
    return db.get('chats', ident)


def turn(db, chat, text, attachments, settings, parent=None):
    now, mid, aid, rid = time.time(), new(), new(), new()
    value = db.get('chats', chat)
    parts = [{'type': 'text', 'text': text}]
    if attachments:
        parts.append({'type': 'images', 'images': attachments})
    with db.transaction():
        for image in attachments:
            db.reference(chat, image)
        db.insert('messages', id=mid, chat_id=chat, parent_id=parent or value['tip'], role='user',
                  parts_json=encode(parts), created=now, run_id=rid)
        db.insert('messages', id=aid, chat_id=chat, parent_id=mid, role='assistant',
                  parts_json='[]', created=now, run_id=rid)
        db.insert('runs', id=rid, chat_id=chat, message_id=mid, assistant_id=aid, status='queued',
                  settings_json=encode(settings), created=now)
        title = ' '.join(text.split())[:64] or 'About an image'
        db.update('chats', chat, tip=aid, updated=now,
                  title=title if value['title'] == 'New chat' else value['title'])
    return {'message_id': mid, 'run_id': rid, 'assistant_id': aid}


def remove(db, chat):
    with db.transaction():
        db.db.execute('UPDATE images SET chat_id=NULL,message_id=NULL WHERE chat_id=?', (chat,))
        for table in ('messages', 'runs', 'image_refs', 'events'):
            db.db.execute(f'DELETE FROM {table} WHERE chat_id=?', (chat,))
        db.db.execute('DELETE FROM chats WHERE id=?', (chat,))
