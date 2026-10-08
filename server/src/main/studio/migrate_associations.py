import json
from .migrate import image_ref
from .store import encode


def attach(db, old, sid, number, assistant):
    end = old.execute("SELECT MIN(id) FROM records WHERE session=? AND kind='chat' AND id>?", (sid,number)).fetchone()[0]
    ids = []
    for row in old.execute("SELECT id,data FROM records WHERE session=? AND kind='image' AND id>? AND id<? ORDER BY id", (sid,number,end or 2**63-1)):
        data = json.loads(row['data'])
        if data.get('actor') == 'assistant':
            ident = image_ref(db, old, sid, row['id'])
            if ident:
                ids.append(ident)
    if ids:
        message = db.get('messages', assistant)
        parts = [*message['parts'], {'type':'images','images':ids}]
        db.update('messages', assistant, parts_json=encode(parts))
        for ident in ids:
            db.update('images', ident, message_id=assistant)
