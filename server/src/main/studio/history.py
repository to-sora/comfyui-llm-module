from .vision_messages import compact
from .history_repair import completed


def rows(e, run):
    parent = e.db.get('messages',run['message_id'])['parent_id']
    return e.db.all('''WITH RECURSIVE chain AS (
        SELECT *,0 AS depth FROM messages WHERE id=? UNION ALL
        SELECT m.*,c.depth+1 FROM messages m JOIN chain c ON m.id=c.parent_id)
        SELECT * FROM chain ORDER BY depth DESC''', (parent,))


def groups(e, run, through):
    result, seen = [], {}
    chain=rows(e,run)
    start=next((i+1 for i,row in enumerate(chain) if row['id']==through),0)
    for row in chain[start:]:
        rid = row.get('run_id')
        if rid and rid in seen:
            seen[rid]['through']=row['id']
            continue
        if rid:
            saved = e.db.get('runs',rid)
            conversation = saved['trace'].get('conversation')
            if conversation:
                messages = completed(compact(conversation))
                if saved['status'] != 'done':
                    messages.append({'role':'user','content':'Earlier request status: '+saved['status']+'. '+(saved['error'] or '')})
                group={'through':row['id'],'messages':messages}
                seen[rid]=group
                result.append(group)
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
                if not text and value.get('content'):
                    text.append(value['content'])
                calls.extend(value.get('tool_calls',[]))
        if text or calls:
            message = {'role':row['role'],'content':'\n'.join(text)}
            if calls:
                message['tool_calls'] = calls
            result.append({'through':row['id'],'messages':[message]})
    return result
