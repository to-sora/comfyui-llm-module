from .chat_images import attach
from .chat_request import complete
from .discovery import llm_settings
from .records import create, get, update
from .settings import APP, read
from .chat_context import build
from .chat_memory import summary
from .base_chat import prepare


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
        from .base_chat import is_base
        batch_id = get(e.db, sid, ident).get("batch")
        if is_base(e, settings["model"]) and batch_id is not None:
            batch = get(e.db, sid, batch_id)
            if batch["status"] == "done" and batch.get("images"):
                from .base_review import inspect
                return await inspect(e, sid, ident, settings, batch["images"])
        context, schema = build(e, sid, ident, messages)
        payload = {**settings, "messages": context, "tools": schema,
                   "temperature": 0, "enable_thinking": False, "parallel_tool_calls": False}
        payload = prepare(e, payload, sid, ident)
        if job.get("intent") == "inspect":
            payload.update(tools=[], tool_choice="none")
            payload["messages"][0]["content"] = "Inspect the actual attached images against the user's requirements. Report visible matches and problems."
        reply = await complete(e, sid, ident, payload)
        message = reply["choices"][0]["message"]
        messages.append(message)
        create(e.db, sid, "message", {**message, "chat": ident})
        calls = message.get("tool_calls", [])
        if not calls:
            if not message.get("content"):
                raise ValueError("Model returned an empty response; no assessment was produced")
            return update(e.db, sid, ident, status="done", response=message.get("content"),
                          usage=reply.get("usage"), memory=await e.comfy.request("/llm/status"))
        for call in calls:
            if get(e.db, sid, ident).get("cancel"):
                raise ValueError("Cancelled")
            function = call["function"]
            if function["name"] == "finish_response":
                from .chat_finish import finish
                return await finish(e, sid, ident, call)
            from .chat_tools import execute
            messages.extend(await execute(e, sid, ident, call))
    raise ValueError("Chat round limit reached. Pending jobs and results are retained.")
