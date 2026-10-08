from .store import encode


def append(e, run, part):
    value = e.db.get('messages', run['assistant_id'])
    parts = value['parts']
    if part['type']=='text' and parts and parts[-1]['type']=='text':
        parts[-1]['text'] += part['text']
    else:
        parts.append(part)
    e.db.update('messages', value['id'], parts_json=encode(parts))


def delta(e, run, text):
    with e.db.transaction():
        append(e, run, {'type':'text','text':text})
        e.publish(run,'message.delta',{'message_id':run['assistant_id'],'text':text})


def pictures(e, run, ids):
    if not ids:
        return
    with e.db.transaction():
        append(e, run, {'type':'images','images':ids})
        e.publish(run,'message.updated',{'message_id':run['assistant_id']})


def separate(e, run):
    value=e.db.get('messages',run['assistant_id'])
    if value['parts'] and value['parts'][-1]['type']=='text':
        delta(e,run,'\n\n')
