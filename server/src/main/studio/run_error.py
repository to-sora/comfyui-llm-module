from .store import encode
from ..errors import UserError, message


def plain(exc):
    text=message(exc)
    if isinstance(exc,UserError):return text
    if 'R2:' in text:
        return 'This assistant was released when another model loaded. Restart ComfyUI to select it again.'
    if any(v in text for v in ('RAM admission','resident budget','Active turns exceed')):
        return 'Not enough RAM to keep these models. Finish active image requests or choose a smaller assistant.'
    if 'out of memory' in text.lower():
        return 'Ran out of GPU memory. Try fewer images or a smaller size.'
    if isinstance(exc,(ConnectionError,TimeoutError)) or 'connect' in text.lower():
        return 'The image engine disconnected. Check its connection and retry.'
    return 'Something went wrong while making this reply. Try again; details are in Debug.'


def mark_images(e,run,text):
    rows=e.db.all("SELECT * FROM images WHERE message_id=? AND kind='generated' AND file IS NULL",(run['assistant_id'],))
    for image in rows:
        e.db.update('images',image['id'],recipe_json=encode({**image['recipe'],'error':text,
            'cancelled':bool(e.db.get('runs',run['id'])['cancelled'])}))
