def completed(messages):
    """Keep interrupted turns valid without pretending their tools finished."""
    result,pending=[],[]
    for message in messages:
        if message['role']!='tool' and pending:
            result.extend({'role':'tool','tool_call_id':ident,
                'content':'This earlier tool call was interrupted before its result was saved.'}
                for ident in pending)
            pending=[]
        if message['role']=='assistant':
            pending=[c['id'] for c in message.get('tool_calls',[])]
        elif message['role']=='tool':
            ident=message.get('tool_call_id')
            if ident in pending:
                pending.remove(ident)
            elif not ident:
                message={**message,'role':'user','content':'Earlier tool result: '+str(message.get('content',''))}
        result.append({k:v for k,v in message.items() if k in ('role','content','tool_calls','tool_call_id','name')})
    result.extend({'role':'tool','tool_call_id':ident,
        'content':'This earlier tool call was interrupted before its result was saved.'} for ident in pending)
    return result
