from .agent_prompt import SYSTEM,inventory
from .agent_tools import prepare,execute_all,repair
from .tool_schema import schemas
from .context import budget
from .llm import complete
from .vision_messages import attach,compact
from .message_parts import delta,separate
from .store import encode
from ..settings import read
from ..errors import UserError


def remember(e,run,current):
    trace=e.db.get('runs',run['id'])['trace']
    trace['conversation']=current
    e.db.update('runs',run['id'],trace_json=encode(trace))


async def run(e,run):
    if not e.caps:
        raise UserError('The image engine is disconnected. Try again when it reconnects.')
    row=e.db.get('messages',run['message_id'])
    text='\n'.join(p['text'] for p in row['parts'] if p['type']=='text')
    ids=[i for p in row['parts'] if p['type']=='images' for i in p['images']]
    current=[await attach(e,run['chat_id'],ids,text)]
    system={'role':'system','content':SYSTEM}
    tools=schemas(e.caps)
    repaired=False
    try:
        for round_no in range(read()['max_chat_rounds']):
            e.check(run)
            remember(e,run,current)
            notes={'role':'user','content':'Images available in this chat:\n'+inventory(e,run)}
            messages=await budget(e,run,system,[notes]+current,tools)
            answer=await complete(e,run,messages,tools)
            clean={k:v for k,v in answer.items() if k in ('role','content','tool_calls')}
            current.append(clean)
            calls=answer.get('tool_calls',[])
            try:
                if answer.get('tool_parse_error'):
                    raise UserError(answer['tool_parse_error'])
                if not calls:
                    if not answer.get('content'):
                        raise UserError('The assistant returned an empty reply. Try again.')
                    return
                tasks,results=prepare(e,run,calls)
            except UserError as exc:
                if repaired:
                    raise UserError('The assistant could not format its image request. Try again.') from exc
                repaired=True
                current.extend(repair(clean,exc))
                separate(e,run)
                continue
            current=compact(current)
            replies,images=await execute_all(e,run,calls,tasks,results)
            current.extend(replies)
            e.publish(run,'tool.started',{'message':'Checking the finished images'})
            current.append(await attach(e,run['chat_id'],images,
                'Check these final results against the request, then answer. Report any problems.'))
        delta(e,run,'\nThe reply reached its step limit. Finished images are saved above; the remaining work was not completed.')
    finally:
        remember(e,run,current)
