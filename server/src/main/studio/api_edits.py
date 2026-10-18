import asyncio
from aiohttp import web
from PIL import Image
from ..errors import json_body,UserError
from ..assets import check_size
from .basic_edits import apply,OPERATIONS
from .image_store import load,reserve,save,metadata
from .image_changes import record


def install(routes,e):
    @routes.get('/api/image-edits')
    async def operations(request):
        return web.json_response({'operations':OPERATIONS,'max_dimension':4096})

    @routes.post('/api/images/{id}/edit')
    async def edit(request):
        source=request.match_info['id']
        body=await json_body(request)
        picture=load(e.db,source)
        try:
            result=await asyncio.to_thread(apply,picture,body)
        except (ValueError,TypeError,OverflowError) as exc:
            raise UserError('Check the values for this image edit') from exc
        return web.json_response(record(e,source,result,body,body.get('chat_id')))

    @routes.post('/api/images/{id}/outpaint')
    async def outpaint(request):
        source=request.match_info['id']
        body=await json_body(request)
        picture=load(e.db,source)
        amounts=[body.get(k,128) for k in ('left','top','right','bottom')]
        if any(type(v) is not int or not 0<=v<=2048 for v in amounts) or not any(amounts):
            raise UserError('Expand one or more edges by 1–2048 pixels')
        left,top,right,bottom=amounts
        size=(picture.width+left+right,picture.height+top+bottom)
        check_size(size)
        canvas=picture.resize(size,Image.Resampling.LANCZOS)
        canvas.paste(picture,(left,top))
        item=record(e,source,canvas,{'operation':'expand_canvas','edges':amounts})
        mask=Image.new('L',size,255)
        mask.paste(0,(left,top,left+picture.width,top+picture.height))
        ident=reserve(e.db,None,None,{'operation':'outpaint_mask'},[item['id']],kind='mask')
        save(e.db,ident,mask)
        return web.json_response({'source':item,'mask':metadata(e.db,ident)})
