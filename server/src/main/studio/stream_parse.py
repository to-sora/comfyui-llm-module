import json


async def packets(response):
    async for raw in response.content:
        line = raw.decode().strip()
        if not line.startswith('data:'):
            continue
        text = line[5:].strip()
        if text == '[DONE]':
            return
        yield json.loads(text)


def merge(message, delta):
    if delta.get('content'):
        message['content'] = (message.get('content') or '') + delta['content']
    for field in ('tool_parse_error','raw_output'):
        if field in delta:
            message[field] = delta[field]
    for call in delta.get('tool_calls', []):
        calls = message.setdefault('tool_calls', [])
        index = call.get('index', 0)
        while len(calls) <= index:
            calls.append({'id':'','type':'function','function':{'name':'','arguments':''}})
        value = calls[index]
        if call.get('id'):
            value['id'] = call['id']
        for field in ('name','arguments'):
            value['function'][field] += call.get('function', {}).get(field, '')
