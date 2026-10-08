import logging
from urllib.parse import urlencode
from .image_store import save
from .store import encode
from ..assets import decode


async def backfill(db,comfy):
    changed=False
    for row in db.all('SELECT * FROM images WHERE deleted=0 AND file IS NULL'):
        recipe=row['recipe']
        remote=recipe.get('legacy',{}).get('remote')
        if not remote:
            continue
        try:
            raw=await comfy.request('/view?'+urlencode(remote),binary=True)
            recipe.pop('import_error',None)
            save(db,row['id'],decode(raw),raw,recipe_json=encode(recipe))
            changed=True
        except Exception as exc:
            logging.exception('Could not restore legacy image %s',row['id'])
            db.update('images',row['id'],recipe_json=encode({**recipe,'import_error':str(exc) or 'Image unavailable'}))
    if changed:
        from .migrate import migrate
        await migrate(db,comfy)
