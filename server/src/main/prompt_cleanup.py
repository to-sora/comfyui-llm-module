import asyncio
import logging


async def cleanup(comfy, prompt_id, completed, future=None):
    try:
        if not completed:
            await asyncio.shield(comfy.cancel(prompt_id))
    except Exception:
        logging.exception("Could not cancel unfinished ComfyUI prompt %s", prompt_id)
    finally:
        comfy.events.pending.pop(prompt_id, None)
        comfy.cancelled.discard(prompt_id)
        if future and not future.done():
            future.cancel()
        elif future and not future.cancelled():
            future.exception()
