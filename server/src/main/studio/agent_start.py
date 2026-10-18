from .agent_prompt import SYSTEM
from .vision_messages import attach
from .tool_schema import schemas
from ..errors import UserError


async def prepare(e,run):
    if not e.caps:
        raise UserError('The image engine is disconnected. Try again when it reconnects.')
    row=e.db.get('messages',run['message_id'])
    text='\n'.join(p['text'] for p in row['parts'] if p['type']=='text')
    from .documents import context
    text+=context(e,row,run['settings'])
    ids=[i for p in row['parts'] if p['type']=='images' for i in p['images']]
    current=[await attach(e,run['chat_id'],ids,text)]
    from .message_api_data import preferences
    from .preference_fields import instructions
    system={'role':'system','content':SYSTEM+'\n'+instructions(preferences(e))}
    tools=schemas(e.caps)
    return current,system,tools
