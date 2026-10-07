import json
from .records import flat
from .chat_images import compact


def memory(e, sid):
    row = e.db.sql("SELECT value FROM meta WHERE key=?", ("summary:" + sid,)).fetchone()
    return json.loads(row[0]) if row else {"through": -1, "text": ""}


def turns(e, sid, ident, through):
    grouped = {}
    for m in flat(e.db, sid, "message"):
        if m["id"] <= through or m.get("chat") == ident:
            continue
        value = {k: m[k] for k in ("role", "content", "tool_calls", "tool_call_id") if k in m}
        value = compact(value)
        if m.get("images"):
            value["content"] = str(value.get("content", "")) + "\nImages: " + ", ".join(f"image {i}" for i in m["images"])
        group = grouped.setdefault(m.get("chat", m["id"]), {"through": m["id"], "messages": []})
        group["through"] = max(group["through"], m["id"])
        group["messages"].append(value)
    return list(grouped.values())


def remember(e, sid, through, text):
    e.db.sql("INSERT OR REPLACE INTO meta VALUES(?,?)", ("summary:" + sid,
             json.dumps({"through": through, "text": text})))
