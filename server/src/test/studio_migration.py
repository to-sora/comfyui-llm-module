import sqlite3
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from studio_helpers import ROOT,record
sys.path.insert(0,str(ROOT))
from server.src.main.studio.store import Store
from server.src.main.studio.chat_store import turn
from server.src.main.studio.history import groups,rows
from server.src.main.studio.migrate_content import restore_text

with tempfile.TemporaryDirectory(dir=ROOT/'server/data/tmp') as folder:
    path=Path(folder)/'studio.sqlite'
    with sqlite3.connect('file:'+str(ROOT/'server/data/studio.sqlite')+'?mode=ro',uri=True) as source:
        with sqlite3.connect(path) as target: source.backup(target)
    db=Store(path)
    try:
        restore_text(db)
        first=db.all("SELECT parts_json FROM messages")
        restore_text(db)
        assert first==db.all("SELECT parts_json FROM messages")
        legacy=db.all("SELECT m.* FROM messages m JOIN legacy l ON l.id=m.id AND l.kind='message'")
        structured=[m for m in legacy if any(p['type']=='legacy' and isinstance(p['value'].get('content'),list) for p in m['parts'])]
        assert structured and all(any(p['type']=='text' for p in m['parts']) for m in structured)
        e=SimpleNamespace(db=db)
        checked=0
        for chat in db.all("SELECT id FROM legacy WHERE kind='chat'"):
            result=turn(db,chat['id'],'What did we discuss?',[],{})
            run=db.get('runs',result['run_id'])
            chain=rows(e,run)
            history=groups(e,run,'')
            assert all(g['through'] in {m['id'] for m in chain} for g in history)
            for index,group in enumerate(history):
                assert groups(e,run,group['through'])==history[index+1:]
            checked+=1
        assert db.db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
        assert not db.all('PRAGMA foreign_key_check')
        record('migration',{'status':'PASS','real_database_copy':True,'legacy_chats':checked,
            'legacy_messages':len(legacy),'structured_content_visible':len(structured),
            'history_cursors_in_chain':True,'idempotent_content_restore':True})
        print('Real legacy data, visible structured content, history cursors and database integrity PASS')
    finally:
        db.db.close()
