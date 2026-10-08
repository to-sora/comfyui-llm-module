import json
from .history import groups
from .llm import complete
from ..errors import UserError


async def budget(e, run, system, current, tools):
    saved = e.db.get('chats',run['chat_id'])
    older = groups(e,run,saved['summary_through'])
    limit = run['settings']['context_tokens'] - run['settings']['max_tokens'] - 64
    async def count(messages, schema):
        result = await e.comfy.request('/llm/token_count',{'model':run['settings']['model'],
            'messages':messages,'tools':schema,'max_tokens':1})
        return result['tokens']
    while True:
        summary = [{'role':'user','content':'Earlier conversation summary:\n'+saved['summary']}] if saved['summary'] else []
        messages = [system]+summary+[m for group in older for m in group['messages']]+current
        if await count(messages,tools) <= limit:
            return messages
        if not older:
            raise UserError('This turn is too large for the assistant context. Shorten it or increase the context in Settings.')
        group = older.pop(0)
        prompt = [{'role':'system','content':'Update a concise factual conversation summary. Preserve user preferences, image numbers, requested changes, decisions, unfinished work and failures. Do not invent facts.'},
            {'role':'user','content':'Previous summary:\n'+saved['summary']+'\nOlder turn:\n'+json.dumps(group['messages'],ensure_ascii=False)}]
        if await count(prompt,[]) > run['settings']['context_tokens']-768:
            raise UserError('An earlier turn is too large to summarize. Increase the assistant context in Settings.')
        answer = await complete(e,run,prompt,[],visible=False,max_tokens=512)
        if not answer.get('content'):
            raise RuntimeError('The assistant returned an empty conversation summary')
        saved = e.db.update('chats',run['chat_id'],summary=answer['content'],summary_through=group['through'])
        e.publish(run,'chat.summary',{'message':'Older messages have been summarized. The full conversation is still saved.'})
