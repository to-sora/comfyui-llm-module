def snapshot(status, model):
    return next(({k: m[k] for k in ("model", "source", "backend", "quantization", "kv_quantization")
                  if k in m} for m in status["models"] if m["model"] == model and m["loaded"]), {})


def actor(e, sid, inline):
    from .records import get
    if inline and e.active and e.active["kind"] == "chat":
        chat = get(e.db, sid, e.active["id"])
        return {"type": "assistant", "chat": chat["id"], "actual": chat.get("actual_model", {})}
    return {"type": "manual"}
