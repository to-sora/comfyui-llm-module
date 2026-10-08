async def cancel(e,ident):
    run=e.db.get('runs',ident)
    if run['status'] not in ('queued','running') or run['cancelled']:
        return run
    e.db.update('runs',ident,cancelled=1)
    for prompt in list(e.prompts[ident]):
        await e.comfy.cancel(prompt)
        entry=e.comfy.events.pending.get(prompt)
        if entry and not entry[0].done():
            entry[0].cancel()
    e.wake.set()
    return e.db.get('runs',ident)
