import logging
from .errors import message
import json
from . import tools
from .chat_images import attach
from .chat_context import brief
from .records import create


async def execute(e, sid, ident, call):
    function = call["function"]
    try:
        args = json.loads(function["arguments"])
        result = brief(await tools.invoke(e, sid, function["name"], args, inline=True))
    except Exception as exc:
        logging.exception("Worker failed")
        result = create(e.db, sid, "result", {"error": message(exc)})
    content = json.dumps(result, ensure_ascii=False)
    msg = {"role": "tool", "tool_call_id": call["id"], "content": content}
    messages = [msg]
    create(e.db, sid, "message", {**msg, "name": function["name"], "chat": ident})
    if result.get("images"):
        messages.append(await attach(e, sid, result["images"], "Inspect these actual results."))
    return messages
