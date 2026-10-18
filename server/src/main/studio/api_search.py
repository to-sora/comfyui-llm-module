from aiohttp import web


def install(routes,e):
    @routes.get('/api/search')
    async def search(request):
        q=request.query.get('q','').strip()[:200]
        if not q:
            return web.json_response({'chats':[],'messages':[],'images':[]})
        chats=e.db.all('SELECT id,title,archived FROM chats WHERE instr(lower(title),lower(?)) ORDER BY updated DESC LIMIT 30',(q,))
        messages=e.db.all('''SELECT m.*,c.title FROM messages m JOIN chats c ON c.id=m.chat_id
            WHERE m.role IN ('user','assistant') AND instr(lower(m.parts_json),lower(?))
            ORDER BY m.id DESC LIMIT 40''',(q,))
        for row in messages:
            row['excerpt']='\n'.join(p['text'] for p in row.pop('parts') if p['type']=='text')[:400]
        images=e.db.all('''SELECT id,chat_id,recipe_json,width,height FROM images
            WHERE deleted=0 AND kind!='mask' AND file IS NOT NULL
            AND instr(lower(recipe_json),lower(?)) ORDER BY id DESC LIMIT 40''',(q,))
        return web.json_response({'chats':chats,'messages':messages,'images':images})
