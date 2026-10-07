import asyncio
import logging


async def cleanup(link, prompt_id, completed, future):
    try:
        if not completed:
            await link.cancel(prompt_id)
        while future and not future.terminal.is_set():
            queue = await link.request("/queue")
            if not any(row[1] == prompt_id for row in queue["queue_running"]):
                break
            try:
                await asyncio.wait_for(future.terminal.wait(), 30)
            except TimeoutError:
                continue
        await link.request("/history", {"delete": [prompt_id]})
    except Exception:
        logging.exception("ComfyUI prompt cleanup failed: %s", prompt_id)
    finally:
        link.events.pending.pop(prompt_id, None)
        if future and not future.done():
            future.cancel()
        elif future and not future.cancelled():
            future.exception()
