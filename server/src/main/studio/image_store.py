import hashlib
import io
import time
from PIL import Image
from ..settings import DATA
from ..assets import decode, png
from ..errors import UserError
from .ids import new
from .store import encode


def metadata(db, ident, chat=None):
    value = db.get('images', ident)
    if value['deleted']:
        raise UserError('This image was deleted')
    if chat:
        ref = db.one('SELECT number FROM image_refs WHERE chat_id=? AND image_id=?', (chat, ident))
        if not ref:
            raise UserError('Attach this image to the chat before using it')
        value['number'] = ref['number']
    return value


def load(db, ident, chat=None):
    item = metadata(db, ident, chat)
    if not item['file']:
        raise UserError('This image has not finished yet')
    return decode((DATA / 'assets' / item['file']).read_bytes())


def reserve(db, chat, message, recipe, parents=None, kind='generated'):
    ident = new()
    db.insert('images', id=ident, chat_id=chat, message_id=message, created=time.time(),
              recipe_json=encode(recipe), parents_json=encode(parents or []), kind=kind, bytes=0)
    if chat:
        db.reference(chat, ident)
    return ident


def save(db, ident, image, raw=None, **extra):
    if max(image.size) > 4096:
        image.thumbnail((4096, 4096), Image.Resampling.LANCZOS)
        raw = None
    raw = png(image) if raw is None else raw
    path, thumb = ident+'.png', ident+'.webp'
    (DATA / 'assets' / path).write_bytes(raw)
    preview = image.copy()
    preview.thumbnail((384, 384))
    preview.save(DATA / 'thumbs' / thumb, format='WEBP')
    return db.update('images', ident, file=path, thumb=thumb, width=image.width, height=image.height,
                     sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw), **extra)


def number(db, chat, value):
    if type(value) is not int:
        raise UserError('Use an image number from this chat')
    ref = db.one('SELECT image_id FROM image_refs WHERE chat_id=? AND number=?', (chat, value))
    if not ref:
        raise UserError(f'Image {value} is not available in this chat')
    return metadata(db, ref['image_id'], chat)


def vision(db, ident, chat):
    metadata(db,ident,chat)
    cache = DATA/'vision'/(ident+'.jpg')
    cache.parent.mkdir(exist_ok=True)
    if cache.is_file():
        return cache.read_bytes()
    picture = load(db, ident, chat).convert('RGB')
    picture.thumbnail((512, 512), Image.Resampling.LANCZOS)
    stream = io.BytesIO()
    picture.save(stream, format='JPEG', quality=85)
    cache.write_bytes(stream.getvalue())
    return stream.getvalue()
