from .store import encode


def restore_text(db):
    """Expose text retained inside old multimodal message records."""
    with db.transaction():
        for row in db.all("SELECT m.* FROM messages m JOIN legacy l ON l.id=m.id AND l.kind='message'"):
            parts=row['parts']
            if any(p['type']=='text' for p in parts):
                continue
            text=[]
            for part in parts:
                if part['type']=='legacy':
                    content=part['value'].get('content')
                    if isinstance(content,list):
                        text.extend(p['text'] for p in content if p.get('type')=='text')
            if text:
                db.update('messages',row['id'],parts_json=encode([
                    {'type':'text','text':'\n'.join(text)},*parts]))
