import json
from .transcript import memory, turns, remember
from .chat_request import complete
from .errors import UserError


async def budget(e, sid, ident, payload):
    saved = memory(e, sid)
    older = turns(e, sid, ident, saved["through"])
    current = payload["messages"]
    async def size(messages, tools=None):
        result = await e.comfy.request("/llm/token_count", {"model": payload["model"], "messages": messages,
            "tools": payload.get("tools", []) if tools is None else tools})
        return result["tokens"]
    allowance = payload["context_tokens"] - payload["max_tokens"] - 64
    while True:
        summary = [{"role": "system", "content": "Earlier conversation summary:\n" + saved["text"]}] if saved["text"] else []
        messages = current[:1] + summary + [m for group in older for m in group["messages"]] + current[1:]
        if await size(messages) <= allowance:
            return {**payload, "messages": messages}
        if not older:
            raise UserError("This turn is too large for the assistant's context. Shorten it or select a larger context.")
        group = older.pop(0)
        summary_prompt = [{"role": "system", "content": "Update a concise factual conversation summary. Preserve user preferences, image numbers and descriptions, decisions, unresolved work and failures. Do not invent facts."},
            {"role": "user", "content": "Previous summary:\n" + saved["text"] + "\nOlder turn:\n" + json.dumps(group["messages"], ensure_ascii=False)}]
        if await size(summary_prompt, []) > payload["context_tokens"] - 768:
            raise UserError("An earlier turn exceeds the summary budget. Increase the assistant context to continue.")
        reply = await complete(e, sid, ident, {**payload, "messages": summary_prompt, "tools": [],
                                              "max_tokens": 512, "temperature": 0})
        text = reply["choices"][0]["message"].get("content")
        if not text:
            raise RuntimeError("The assistant returned an empty conversation summary")
        saved = {"through": group["through"], "text": text}
        remember(e, sid, **saved)
