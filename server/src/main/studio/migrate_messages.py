import json
from .ids import new
from .store import encode
from .migrate import mapped, link, image_ref


def migrate_messages(db, old):
    with db.transaction():
        for row in old.execute("SELECT * FROM records WHERE kind='message' ORDER BY created,id"):
            sid, number = row['session'], row['id']
            if mapped(db, 'message', sid, number):
                continue
            chat = mapped(db, 'chat', sid, -1)
            current = db.one('SELECT * FROM chats WHERE id=?', (chat,))
            if not current:
                continue
            value = json.loads(row['data'])
            content = value.get('content')
            parts = [{'type': 'text', 'text': content}] if isinstance(content, str) and content else []
            images = [image_ref(db, old, sid, n) for n in value.get('images', [])]
            for image in filter(None, images):
                db.reference(chat, image)
            if any(images):
                parts.append({'type': 'images', 'images': [i for i in images if i]})
            if value.get('tool_calls') or value.get('role') == 'tool' or isinstance(content, list):
                parts.append({'type': 'legacy', 'value': value})
            ident = new()
            db.insert('messages', id=ident, chat_id=chat, parent_id=current['tip'],
                      role=value.get('role', 'assistant'), parts_json=encode(parts), created=row['created'])
            db.update('chats', chat, tip=ident, updated=row['created'])
            link(db, 'message', sid, number, ident)
