import hashlib
import json
import logging
from urllib.parse import urlencode
from PIL import Image
from ..settings import DATA
from ..assets import decode
from .ids import new
from .store import encode
from .migrate import mapped, link, image_ref
from .image_store import reserve, save


async def migrate_images(db, old, comfy):
    rows = list(old.execute("SELECT * FROM records WHERE kind='image' ORDER BY created"))
    for row in rows:
        sid, number = row['session'], row['id']
        if mapped(db, 'image', sid, number):
            continue
        chat = mapped(db, 'chat', sid, -1)
        if not db.one('SELECT id FROM chats WHERE id=?', (chat,)):
            continue
        value = json.loads(row['data'])
        recipe = {**value.get('settings', {}), 'operation': value['operation'], 'legacy': value}
        with db.transaction():
            ident = reserve(db, chat, None, recipe, kind='mask' if value['operation']=='mask' else
                            'upload' if value['operation']=='upload' else 'generated')
            db.update('images', ident, created=row['created'], deleted=int(value.get('deleted', False)))
            db.db.execute('UPDATE image_refs SET number=? WHERE chat_id=? AND image_id=?', (number, chat, ident))
            link(db, 'image', sid, number, ident)
        if value.get('deleted'):
            continue
        try:
            if value.get('file'):
                raw = (DATA/'assets'/value['file']).read_bytes()
                picture = decode(raw)
                thumb = ident+'.webp'
                picture.thumbnail((384, 384))
                picture.save(DATA/'thumbs'/thumb, format='WEBP')
                db.update('images', ident, file=value['file'], thumb=thumb, width=value['width'],
                          height=value['height'], bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
            else:
                raw = await comfy.request('/view?'+urlencode(value['remote']), binary=True)
                save(db, ident, decode(raw), raw)
        except Exception as exc:
            logging.exception('Legacy image could not be copied: %s/%s', sid, number)
            db.update('images', ident, recipe_json=encode({**recipe, 'import_error': str(exc) or 'Image unavailable'}))
    with db.transaction():
        for row in rows:
            ident = mapped(db, 'image', row['session'], row['id'])
            if ident:
                parents = [image_ref(db, old, row['session'], p) for p in json.loads(row['data']).get('parents', [])]
                db.update('images', ident, parents_json=encode([p for p in parents if p]))
