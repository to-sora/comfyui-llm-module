from aiohttp import web
from .branches import chain
from .store import encode
from .zip_response import send
from ..settings import DATA


def transcript(e,chat):
    title=e.db.get('chats',chat)['title']
    lines=['# '+title,'']
    ids=[]
    for row in chain(e.db,chat):
        lines.extend(['## '+('You' if row['role']=='user' else 'Studio'),''])
        for p in row['parts']:
            if p['type']=='text':
                lines.extend([p['text'],''])
            elif p['type']=='documents':
                for ident in p['documents']:
                    doc=e.db.one('SELECT name,file FROM documents WHERE id=?',(ident,))
                    if doc:
                        lines.extend(['['+doc['name']+'](documents/'+doc['file']+')',''])
            elif p['type']=='images':
                for ident in p['images']:
                    item=e.db.get('images',ident)
                    if item['file'] and not item['deleted'] and item['kind']!='mask':
                        ids.append(ident)
                        lines.extend([f'![Image {ident}](images/{ident}.png)',''])
    return '\n'.join(lines),list(dict.fromkeys(ids))


def install(routes,e):
    @routes.get('/api/chats/{id}/export')
    async def export(request):
        chat=request.match_info['id']
        text,ids=transcript(e,chat)
        if request.query.get('format')=='md':
            return web.Response(text=text,content_type='text/markdown',headers={
                'Content-Disposition':f'attachment; filename="chat-{chat}.md"'})
        items=[e.db.get('images',i) for i in ids]
        files=[('images/'+r['id']+'.png',DATA/'assets'/r['file']) for r in items]
        docs={i for row in chain(e.db,chat) for p in row['parts'] if p['type']=='documents' for i in p['documents']}
        for ident in docs:
            doc=e.db.one('SELECT file FROM documents WHERE id=?',(ident,))
            if doc:
                files.append(('documents/'+doc['file'],DATA/'documents'/doc['file']))
        return await send(request,'chat-'+chat+'.zip',files,{'conversation.md':text,
                          'recipes.json':encode(items)})
