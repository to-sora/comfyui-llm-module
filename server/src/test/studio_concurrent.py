import asyncio
import aiohttp
from studio_helpers import record


async def main():
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as client:
        async def request(path,data=None):
            async with client.request('POST' if data is not None else 'GET',
                    'https://127.0.0.1:8189/api'+path,json=data) as response:
                value=await response.json()
                assert response.status==200,value
                return value
        chats=await asyncio.gather(*(request('/chats',{}) for _ in range(2)))
        first,second=await asyncio.gather(*(request('/chats/'+chat['id']+'/messages',
            {'text':text,'attachments':[]}) for chat,text in zip(chats,[
                'Show a Markdown table comparing red and blue, then a short Python code block printing hello.',
                'What is 6 times 7? Reply with only the number.'])))
        states=[await request('/debug/runs/'+r['run_id']) for r in (first,second)]
        assert sum(s['status']=='running' for s in states)<=1
        for _ in range(180):
            await asyncio.sleep(1)
            states=[await request('/debug/runs/'+r['run_id']) for r in (first,second)]
            if all(s['status'] not in ('running','queued') for s in states):
                break
        messages=[await request('/chats/'+c['id']+'/messages') for c in chats]
        record('concurrent',{'runs':states,'messages':messages})
        assert all(s['status']=='done' for s in states),states
        assert states[1]['started']>=states[0]['finished'],[(s['started'],s['finished']) for s in states]
        answer=''.join(p['text'] for m in messages[1]['messages'] if m['role']=='assistant' for p in m['parts'] if p['type']=='text')
        assert answer.strip()=='42',answer
        assert all(all(m['chat_id']==c['id'] for m in value['messages']) for c,value in zip(chats,messages))
        record('concurrent-result',{'passed':True,'chats':[c['id'] for c in chats],
            'one_gpu_run':True,'answer':answer,'isolated_messages':True})
        print('Concurrent chats passed',flush=True)


asyncio.run(main())
