import json
from .tool_plan import plan
from .image_batch import execute
from .image_store import metadata
from .message_parts import pictures
from .store import encode
from ..errors import UserError


def prepare(e, run, calls):
    try:
        with e.db.transaction():
            tasks, results = plan(e,run,calls)
            if len(tasks)>32:
                raise UserError('Please request at most 32 images in one turn')
    except (ValueError, TypeError, AttributeError) as exc:
        raise UserError('Invalid image tool arguments: '+str(exc)) from exc
    return tasks,results


async def execute_all(e, run, calls, tasks, results):
    pictures(e,run,[t['id'] for t in tasks])
    e.publish(run,'tool.started',{'message':'Making your images','count':len(tasks)})
    e.trace(run,'tools',{'calls':calls,'images':results})
    await execute(e,run,tasks)
    replies, visible = [], []
    for call in calls:
        images = []
        for ident in results[call['id']]:
            item = metadata(e.db,ident,run['chat_id'])
            value = {'image':item['number'],'status':'done' if item['file'] else 'failed'}
            if item['file']:
                visible.append(ident)
                value.update(width=item['width'],height=item['height'])
            else:
                value['error']=item['recipe'].get('error','Image not completed')
            images.append(value)
        replies.append({'role':'tool','tool_call_id':call['id'],
                        'content':encode({'images':images})})
    # Inspect final descendants, retaining unrelated results in the same batch.
    parents={p for ident in visible for p in metadata(e.db,ident)['parents']}
    return replies,list(dict.fromkeys(i for i in visible if i not in parents))


def repair(message, error):
    calls=message.get('tool_calls') or []
    if calls:
        return [{'role':'tool','tool_call_id':call['id'],
            'content':encode({'error':str(error),'executed':False})} for call in calls]
    return [{'role':'user','content':'The tool call could not be parsed: '+str(error)+
        '. Return valid JSON arguments using the listed tools. Do not repeat explanation.'}]
