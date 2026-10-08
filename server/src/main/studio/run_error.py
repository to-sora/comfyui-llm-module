from .store import encode


def mark_images(e,run,text):
    rows=e.db.all("SELECT * FROM images WHERE message_id=? AND kind='generated' AND file IS NULL",(run['assistant_id'],))
    for image in rows:
        e.db.update('images',image['id'],recipe_json=encode({**image['recipe'],'error':text,
            'cancelled':bool(e.db.get('runs',run['id'])['cancelled'])}))
