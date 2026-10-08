import json
import sqlite3
from ..settings import DATA
from .ids import new
from .store import encode


def mapped(db, kind, session, number):
    row = db.one('SELECT id FROM legacy WHERE kind=? AND session=? AND number=?', (kind, session, number))
    return row['id'] if row else None


def link(db, kind, session, number, ident):
    db.insert('legacy', kind=kind, session=session, number=number, id=ident)


async def migrate(db, comfy):
    source = DATA / 'workbench.sqlite'
    if not source.is_file():
        return
    old = sqlite3.connect(source.as_uri()+'?mode=ro', uri=True)
    old.row_factory = sqlite3.Row
    try:
        with db.transaction():
            for row in old.execute('SELECT * FROM sessions ORDER BY created'):
                if mapped(db, 'chat', row['id'], -1):
                    continue
                ident = new()
                settings = json.loads(row['settings'])
                if settings.get('model') == 'gemma-4-E2B':
                    settings['model'] = 'gemma-3-12b-it'
                settings.update(backend='transformers')
                if settings.get('kv_quantization') in ('q8_0', 'q4_0'):
                    settings['kv_quantization'] = 'hqq_'+settings['kv_quantization'][1]
                db.insert('chats', id=ident, title=row['name'], created=row['created'],
                          updated=row['created'], settings_json=encode(settings))
                link(db, 'chat', row['id'], -1, ident)
        from .migrate_images import migrate_images
        await migrate_images(db, old, comfy)
        from .migrate_aliases import migrate_aliases
        migrate_aliases(db,old)
        from .migrate_messages import migrate_messages
        migrate_messages(db, old)
        from .migrate_runs import migrate_runs
        migrate_runs(db, old)
        from .migrate_content import restore_text
        restore_text(db)
    finally:
        old.close()


def image_ref(db, old, sid, number):
    ident = mapped(db, 'image', sid, number)
    if ident:
        return ident
    alias = old.execute('SELECT owner,target FROM aliases WHERE session=? AND id=?', (sid, number)).fetchone()
    if alias:
        return mapped(db, 'image', alias['owner'], alias['target'])
    job = old.execute("SELECT data FROM records WHERE session=? AND id=? AND kind='job'", (sid, number)).fetchone()
    if job:
        return mapped(db, 'image', sid, json.loads(job[0]).get('image', -1))
