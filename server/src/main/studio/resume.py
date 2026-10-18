from .store import encode
from .branches import idle
from .run_worker import notify
from .image_batch import execute
from .vision_messages import attach
from .message_parts import separate
from .image_store import metadata
from ..errors import UserError


def enqueue_resume(e, ident):
    run=e.db.get('runs',ident)
    idle(e,run['chat_id'])
    if run['status'] not in ('failed','cancelled','interrupted'):
        raise UserError('This reply has already finished')
    trace=run['trace']
    trace['resume']=True
    e.db.update('runs',ident,status='queued',cancelled=0,error=None,finished=None,trace_json=encode(trace))
    e.db.update('chats',run['chat_id'],tip=run['assistant_id'])
    notify(e)
    e.wake.set()
    return {'run_id':ident}


async def prepare(e,run):
    from .agent_start import prepare as start
    current,system,tools=await start(e,run)
    rows=e.db.all("SELECT * FROM images WHERE message_id=? AND kind='generated' AND deleted=0",(run['assistant_id'],))
    tasks=[{'id':r['id'],'params':{k:v for k,v in r['recipe'].items() if k not in ('error','cancelled')},'call':'resume'}
           for r in rows if not r['file']]
    if tasks:
        for task in tasks:
            e.db.update('images',task['id'],recipe_json=encode(task['params']))
        await execute(e,run,tasks)
    e.check(run)
    done=[metadata(e.db,r['id'],run['chat_id']) for r in rows if e.db.get('images',r['id'])['file']]
    previous=e.db.get('messages',run['assistant_id'])
    partial='\n'.join(p['text'] for p in previous['parts'] if p['type']=='text')
    completed=[{'image':r['number'],'operation':r['recipe'].get('operation'),
                'prompt':r['recipe'].get('requested_prompt',r['recipe'].get('prompt',''))} for r in done]
    current.append(await attach(e,run['chat_id'],[r['id'] for r in done[-8:]],
        'Continue this interrupted request. These images are already finished; do not recreate them. '
        'Use tools only for remaining work. Review the finished results before answering.\n'
        'Completed images: '+encode(completed)+'\nPrevious partial reply: '+partial))
    separate(e,run)
    trace=e.db.get('runs',run['id'])['trace']
    trace['resume']=False
    e.db.update('runs',run['id'],trace_json=encode(trace))
    return current,system,tools
