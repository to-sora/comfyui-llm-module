import logging


async def retain(e,run,tasks):
    from .basic_edits import OPERATIONS
    names = sorted({t['params']['checkpoint'] for t in tasks
                    if t['params'].get('operation') not in ('remove_background','upscale_image',*OPERATIONS)})
    if names:
        await e.comfy.request('/llm/turns/'+run['id'],{'checkpoints':names},method='PUT')


async def release(e,run):
    try:
        await e.comfy.request('/llm/turns/'+run['id'],method='DELETE')
    except Exception:
        logging.exception('Could not release checkpoint references for turn %s',run['id'])
