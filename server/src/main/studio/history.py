from .vision_messages import compact
from .history_repair import completed


def rows(e, run):
    parent = e.db.get('messages',run['message_id'])['parent_id']
    return e.db.all('''WITH RECURSIVE chain AS (
        SELECT * FROM messages WHERE id=? UNION ALL
        SELECT m.* FROM messages m JOIN chain c ON m.id=c.parent_id)
        SELECT * FROM chain ORDER BY id''', (parent,))


def groups(e, run, through):
    result, seen = [], set()
    for row in rows(e,run):
        if row['id'] <= through:
            continue
        rid = row.get('run_id')
        if rid and rid in seen:
            continue
        if rid:
            saved = e.db.get('runs',rid)
            conversation = saved['trace'].get('conversation')
            if conversation:
                seen.add(rid)
                messages = completed(compact(conversation))
                if saved['status'] != 'done':
                    messages.append({'role':'user','content':'Earlier request status: '+saved['status']+'. '+(saved['error'] or '')})
                result.append({'through':saved['assistant_id'],'messages':messages})
                continue
        text, calls = [], []
        for part in row['parts']:
            if part['type']=='text':
                text.append(part['text'])
            elif part['type']=='images':
                for ident in part['images']:
                    ref = e.db.one('SELECT number FROM image_refs WHERE chat_id=? AND image_id=?',(run['chat_id'],ident))
                    if ref:
                        text.append('Image '+str(ref['number']))
            elif part['type']=='legacy':
                value = compact([part['value']])[0]
                calls.extend(value.get('tool_calls',[]))
        if text or calls:
            message = {'role':row['role'],'content':'\n'.join(text)}
            if calls:
                message['tool_calls'] = calls
            result.append({'through':row['id'],'messages':[message]})
    return result
