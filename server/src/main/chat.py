from .chat_images import attach
from .chat_request import complete
from .discovery import llm_settings
from .records import create, get, update
from .settings import APP, read
from .chat_context import build
from .context_budget import budget
from .chat_images import compact


async def run(e, sid, ident):
    job = get(e.db, sid, ident)
    settings = llm_settings(e.caps, job["settings"])
    system = (APP / "config/content-config/assistant.txt").read_text()
    messages = [{"role": "system", "content": system}]
    user = await attach(e, sid, job.get("images", []), job["text"])
    messages.append(user)
    create(e.db, sid, "message", {"role": "user", "content": job["text"], "images": job.get("images", []), "chat": ident})
    repairs = 0
    for step in range(read()["max_chat_rounds"]):
        update(e.db, sid, ident, round=step + 1)
        context, schema = build(e, sid, ident, messages)
        if job.get("intent") == "revise":
            schema = [t for t in schema if t["function"]["name"] != "image_gen_sdxl_text"]
        payload = {**settings, "messages": context, "tools": schema,
                   "temperature": 0, "enable_thinking": False, "parallel_tool_calls": False}
        from .chat_intent import apply
        payload = apply(payload, job)
        payload = await budget(e, sid, ident, payload)
        reply = await complete(e, sid, ident, payload)
        messages[:] = [compact(m) for m in messages]
        message = reply["choices"][0]["message"]
        messages.append(message)
        create(e.db, sid, "message", {**message, "chat": ident})
        if message.get("tool_parse_error"):
            if repairs:
                raise RuntimeError("The assistant could not form a valid tool call after one repair. Please try again.")
            repairs += 1
            messages.append({"role": "user", "content": "Repair your tool call: " + message["tool_parse_error"]})
            continue
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
            from .chat_tools import execute
            messages.extend(await execute(e, sid, ident, call))
    raise ValueError("Chat round limit reached. Pending jobs and results are retained.")
