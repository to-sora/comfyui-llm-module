from .store import encode
from .branches import idle
from .run_worker import notify
from .image_batch import execute
from .vision_messages import attach
from .llm import complete
from .message_parts import separate
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


async def finish(e,run):
    rows=e.db.all("SELECT * FROM images WHERE message_id=? AND kind='generated' AND deleted=0",(run['assistant_id'],))
    tasks=[{'id':r['id'],'params':{k:v for k,v in r['recipe'].items() if k not in ('error','cancelled')},'call':'resume'}
           for r in rows if not r['file']]
    if tasks:
        for task in tasks:
            e.db.update('images',task['id'],recipe_json=encode(task['params']))
        await execute(e,run,tasks)
    e.check(run)
    row=e.db.get('messages',run['message_id'])
    original='\n'.join(p['text'] for p in row['parts'] if p['type']=='text')
    from .documents import context
    original+=context(e,row,run['settings'])
    done=[r['id'] for r in rows if e.db.get('images',r['id'])['file']]
    previous=e.db.get('messages',run['assistant_id'])
    partial='\n'.join(p['text'] for p in previous['parts'] if p['type']=='text')
    current=await attach(e,run['chat_id'],done[-8:],
        'Original request: '+original+'\nPrevious partial reply: '+partial+
        '\nContinue the interrupted reply. Finished images are attached; do not claim unfinished images succeeded.')
    separate(e,run)
    answer=await complete(e,run,[{'role':'system','content':'Finish the user request and review actual images honestly.'},current],[])
    trace=e.db.get('runs',run['id'])['trace']
    from .vision_messages import compact
    trace['conversation']=compact([current,{k:v for k,v in answer.items() if k in ('role','content')}])
    trace['resume']=False
    e.db.update('runs',run['id'],trace_json=encode(trace))
