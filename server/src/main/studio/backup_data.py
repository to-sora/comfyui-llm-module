import json
from pathlib import PurePosixPath
from ..errors import UserError

TABLES=('chats','messages','runs','images','image_refs','preferences','legacy','documents')
FOLDERS=('assets','thumbs','documents')


def manifest(db):
    return {'format':'studio-backup','tables':{t:[dict(row) for row in db.db.execute('SELECT * FROM '+t)] for t in TABLES}}


def read(archive):
    item=archive.getinfo('studio.json')
    if item.file_size>64*1024**2:
        raise UserError('The backup metadata exceeds the 64 MiB restore limit')
    data=json.loads(archive.read(item))
    if data.get('format')!='studio-backup' or not isinstance(data.get('tables'),dict):
        raise UserError('Choose a Studio backup ZIP')
    for info in archive.infolist():
        parts=PurePosixPath(info.filename).parts
        if info.filename=='studio.json':
            continue
        if len(parts)!=2 or parts[0] not in FOLDERS or '..' in parts or '\\' in info.filename:
            raise UserError('The backup contains an unexpected path')
        if info.file_size>128*1024**2:
            raise UserError('A backup asset exceeds the supported image/document size')
    for row in data['tables'].get('images',[]):
        for key in ('file','thumb'):
            if row.get(key) and PurePosixPath(row[key]).name!=row[key]:
                raise UserError('Invalid asset filename in backup')
    for row in data['tables'].get('documents',[]):
        if PurePosixPath(row['file']).name!=row['file']:
            raise UserError('Invalid document filename in backup')
    return data


def merge(db,data):
    counts={}
    with db.transaction():
        for table in TABLES:
            fields={r[1] for r in db.db.execute('PRAGMA table_info('+table+')')}
            count=0
            for raw in data['tables'].get(table,[]):
                row={k:v for k,v in raw.items() if k in fields}
                if table=='runs' and row.get('status') in ('running','queued'):
                    row.update(status='interrupted',cancelled=1,error='Restored unfinished reply; choose Continue.')
                names=','.join(row)
                sql=f'INSERT OR IGNORE INTO {table}({names}) VALUES({",".join("?" for _ in row)})'
                count+=db.db.execute(sql,tuple(row.values())).rowcount
            counts[table]=count
    return counts
