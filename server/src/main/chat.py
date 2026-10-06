import json
from . import tools
from .chat_images import attach, compact
from .chat_request import complete
from .discovery import llm_settings
from .records import create, get, update, flat
from .settings import APP, read
from .chat_context import build, brief
from .chat_memory import summary


async def run(e, sid, ident):
    job = get(e.db, sid, ident)
    settings = llm_settings(e.caps, job["settings"])
    system = (APP / "config/content-config/assistant.txt").read_text() + "\n" + summary(e, sid)
    messages = [{"role": "system", "content": system}]
    user = await attach(e, sid, job.get("images", []), job["text"])
    messages.append(user)
    create(e.db, sid, "message", {"role": "user", "content": job["text"], "images": job.get("images", []), "chat": ident})
    for step in range(read()["max_chat_rounds"]):
        update(e.db, sid, ident, round=step + 1)
        context, schema = build(e, sid, ident, messages)
        payload = {**settings, "messages": context, "tools": schema,
                   "temperature": 0, "enable_thinking": False, "parallel_tool_calls": False}
        reply = await complete(e, sid, ident, payload)
        message = reply["choices"][0]["message"]
        messages.append(message)
        create(e.db, sid, "message", {**message, "chat": ident})
        calls = message.get("tool_calls", [])
        if not calls:
            return update(e.db, sid, ident, status="done", response=message.get("content"),
                          usage=reply.get("usage"), memory=await e.comfy.request("/llm/status"))
        for call in calls:
            if get(e.db, sid, ident).get("cancel"):
                raise ValueError("Cancelled")
            function = call["function"]
            try:
                args = json.loads(function["arguments"])
                result = brief(await tools.invoke(e, sid, function["name"], args, inline=True))
            except Exception as exc:
                result = create(e.db, sid, "result", {"error": str(exc)})
            content = json.dumps(result, ensure_ascii=False)
            msg = {"role": "tool", "tool_call_id": call["id"], "content": content}
            messages.append(msg)
            create(e.db, sid, "message", {**msg, "name": function["name"], "chat": ident})
            if result.get("images"):
                messages.append(await attach(e, sid, result["images"], "Inspect these actual results."))
    raise ValueError("Chat round limit reached. Pending jobs and results are retained.")
