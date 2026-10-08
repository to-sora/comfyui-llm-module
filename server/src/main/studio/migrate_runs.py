import json
from .ids import new
from .store import encode
from .migrate import mapped, link
from .migrate_associations import attach


def migrate_runs(db, old):
    with db.transaction():
        for row in old.execute("SELECT * FROM records WHERE kind='chat' ORDER BY created"):
            sid, n = row['session'], row['id']
            if mapped(db, 'run', sid, n):
                continue
            chat, data = mapped(db, 'chat', sid, -1), json.loads(row['data'])
            if not db.one('SELECT id FROM chats WHERE id=?', (chat,)):
                continue
            ids, transcript = [], []
            for m in old.execute("SELECT id,data FROM records WHERE session=? AND kind='message' ORDER BY id", (sid,)):
                value = json.loads(m['data'])
                if value.get('chat') == n:
                    ids.append(mapped(db, 'message', sid, m['id']))
                    transcript.append(value)
            rid = new()
            if not ids:
                ident = new()
                db.insert('messages', id=ident, chat_id=chat, role='user', created=row['created'],
                          parts_json=encode([{'type': 'text', 'text': data['text']}]))
                ids.append(ident)
            mid = ids[0]
            if db.get('messages', ids[-1])['role'] != 'assistant':
                aid = new()
                db.insert('messages', id=aid, chat_id=chat, parent_id=ids[-1], role='assistant',
                          parts_json='[]', created=row['created'])
                ids.append(aid)
            aid = ids[-1]
            status = data['status'] if data['status'] in ('done','failed','cancelled') else 'interrupted'
            db.insert('runs', id=rid, chat_id=chat, message_id=mid, assistant_id=aid, status=status,
                      settings_json=encode(data.get('settings', {})), created=row['created'],
                      error=data.get('error') or ('This earlier request did not finish' if status!='done' else None),
                      trace_json=encode({'legacy': data, 'conversation': transcript}))
            for ident in ids:
                db.update('messages', ident, run_id=rid)
            attach(db, old, sid, n, aid)
            link(db, 'run', sid, n, rid)
        for image in db.all("SELECT * FROM images WHERE message_id IS NULL AND kind!='mask' AND file IS NOT NULL ORDER BY created"):
            chat = image['chat_id']
            if not chat:
                continue
            current, ident = db.get('chats', chat), new()
            db.insert('messages', id=ident, chat_id=chat, parent_id=current['tip'], role='assistant',
                      parts_json=encode([{'type':'images','images':[image['id']]},
                          {'type':'activity','text':'Imported image'}]), created=image['created'])
            db.update('images', image['id'], message_id=ident)
            db.update('chats', chat, tip=ident)
