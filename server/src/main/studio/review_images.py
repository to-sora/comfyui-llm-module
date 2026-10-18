from .image_store import metadata
from .vision_messages import attach


async def message(e,run,ids):
    final=list(dict.fromkeys(ids))[-8:]
    sources=[]
    notes=[]
    for ident in final:
        item=metadata(e.db,ident,run['chat_id'])
        source=item['recipe'].get('source')
        if source and source not in final and source not in sources:
            parent=metadata(e.db,source,run['chat_id'])
            if parent['file']:
                sources.append(source)
                notes.append(f'Image {parent["number"]} is the source for final image {item["number"]}.')
        if item['recipe'].get('preserved_unmasked_pixels'):
            notes.append(f'Final image {item["number"]}: the compositor preserved every unpainted pixel exactly.')
    sources=sources[:max(0,8-len(final))]
    return await attach(e,run['chat_id'],sources+final,
        'Check the final images against the request. Compare edits only against source pixels shown here. '
        'State visible matches or specific defects briefly. Do not invent a previous background or a change. '
        'If a source is not shown, avoid claiming how it changed.\n'+'\n'.join(notes))
