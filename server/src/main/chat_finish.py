import json
from .records import create, update


async def finish(e, sid, ident, call):
    text = json.loads(call["function"]["arguments"])["text"]
    if not isinstance(text, str):
        raise ValueError("finish_response requires text")
    result = create(e.db, sid, "result", {"response": text})
    create(e.db, sid, "message", {"role": "tool", "name": "finish_response",
        "tool_call_id": call["id"], "content": json.dumps(result), "chat": ident})
    create(e.db, sid, "message", {"role": "assistant", "content": text, "chat": ident})
    return update(e.db, sid, ident, status="done", response=text,
                  memory=await e.comfy.request("/llm/status"))
