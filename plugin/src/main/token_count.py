import asyncio
from aiohttp import web
from .registry import options
from .hf_load import processor
from .hf_inputs import prepare
from .protocol import validate
from .errors import UserError, message
from functools import lru_cache
import logging


@lru_cache(maxsize=8)
def tokenizer(model):
    cfg = options(model)
    if cfg["backend"] != "transformers":
        raise UserError("Import this GGUF model before using it")
    return processor(cfg)


def count(body):
    value, vision = tokenizer(body["model"])
    inputs = prepare(value, vision, body, [])
    return {"tokens": int(inputs["input_ids"].shape[-1])}


def install(routes):
    @routes.post("/llm/token_count")
    async def tokens(request):
        try:
            body = validate(await request.json())
            return web.json_response(await asyncio.to_thread(count, body))
        except UserError as exc:
            return web.json_response({"error": message(exc)}, status=400)
        except Exception as exc:
            logging.exception("Token counting failed")
            return web.json_response({"error": message(exc)}, status=500)
