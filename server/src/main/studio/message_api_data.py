from .image_store import metadata


def page(e,chat,before):
    messages=e.db.all('SELECT * FROM messages WHERE chat_id=? AND id<? ORDER BY id DESC LIMIT 60',
                       (chat,before or 'Z'))[::-1]
    runs,images={},{}
    for row in messages:
        if row['run_id'] and row['run_id'] not in runs:
            run=e.db.get('runs',row['run_id'])
            runs[run['id']]={k:v for k,v in run.items() if k!='trace'}
        for part in row['parts']:
            if part['type']=='images':
                for ident in part['images']:
                    image=e.db.get('images',ident)
                    ref=e.db.one('SELECT number FROM image_refs WHERE chat_id=? AND image_id=?',(chat,ident))
                    image['number']=ref['number'] if ref else None
                    images[ident]=image
    cursor=e.db.one('SELECT COALESCE(MAX(seq),0) AS n FROM events')['n']
    return {'messages':messages,'runs':runs,'images':images,'cursor':cursor,
            'before':messages[0]['id'] if len(messages)==60 else None}


def preferences(e):
    row=e.db.one("SELECT value_json FROM preferences WHERE key='settings'")
    return row['value'] if row else {}
