import time
from studio_helpers import call,record

original=call('/bootstrap')['settings']
chat=call('/chats',{})['id']
prefs={**original,'assistant':{**original['assistant'],'context_tokens':4096,'max_tokens':384},'chat_id':chat}
checks=[]

def turn(text):
    ident=call(f'/chats/{chat}/messages',{'text':text,'attachments':[]})['run_id']
    for _ in range(1200):
        run=call('/debug/runs/'+ident)
        if run['status'] not in ('queued','running'):
            assert run['status']=='done',run.get('error')
            checks.append(run)
            return run
        time.sleep(.5)
    raise TimeoutError('Long-chat turn did not finish')

try:
    call('/settings',prefs,'PUT')
    turn('We are planning an exhibition poster, but do not make images yet. The project code is HARBOUR BLUE, the organizer is Marta, and the main color must be cobalt blue. Never put words in the picture itself. Confirm these four requirements in one sentence.')
    for topic in ('composition','lighting','foreground','background','camera angle','visual rhythm','material textures','print presentation'):
        turn('Still planning only. Write about 220 words comparing two distinct '+topic+' ideas for this poster. Keep our agreed requirements. Do not generate any images.')
        saved=call('/chats/'+chat)
        print(topic,'summary',bool(saved['summary']),flush=True)
        if saved['summary']:
            break
    saved=call('/chats/'+chat)
    assert saved['summary'], 'The realistic planning conversation did not exercise rolling summarization'
    final=turn('Before we proceed, recall the exact project code, organizer, required color, and rule about words in the picture. Answer these four items briefly; do not generate an image.')
    replies=[x for x in final['trace']['steps'] if x['kind']=='assistant']
    answer=replies[-1]['response']['content']
    assert all(word in answer.lower() for word in ('harbour blue','marta','cobalt')),answer
    assert 'word' in answer.lower() or 'text' in answer.lower(),answer
    assert len(call(f'/chats/{chat}/messages')['messages'])>=8
    record('long-memory',{'status':'PASS','chat_id':chat,'summary':saved['summary'],
        'summary_through':saved['summary_through'],'answer':answer,'turns':len(checks)})
    record('long-memory-runs',checks)
    print('Rolling summary and retained conversation facts PASS',flush=True)
finally:
    call('/settings',original,'PUT')
