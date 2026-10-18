import asyncio
import json
import sys
from pathlib import Path
from ..errors import UserError


async def extract(path):
    process=await asyncio.create_subprocess_exec(sys.executable,str(Path(__file__).with_name('document_extract.py')),str(path),
        stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
    try:
        output,error=await asyncio.wait_for(process.communicate(),25)
        if process.returncode:
            raise UserError('This document could not be read within its size/time limit. Use a smaller unlocked PDF or UTF-8 text file.')
        return json.loads(output)
    finally:
        if process.returncode is None:
            process.kill()
            await process.wait()


def get(db,ident):
    value=db.one('SELECT * FROM documents WHERE id=?',(ident,))
    if not value:
        raise UserError('This document is no longer available')
    return value


def context(e,row,settings):
    ids=[i for p in row['parts'] if p['type']=='documents' for i in p['documents']]
    limit=min(40000,max(512,int((settings['context_tokens']-settings['max_tokens']-3000)*.7)))
    parts=[]
    for ident in ids:
        doc=get(e.db,ident)
        maximum=limit//max(1,len(ids))
        text=doc['text'][:maximum]
        note=' (excerpt; document exceeds this turn’s context)' if len(doc['text'])>maximum else ''
        parts.append('\nAttached document: '+doc['name']+note+'\n'+text)
    return '\n'.join(parts)
