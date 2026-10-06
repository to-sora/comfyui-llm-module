import json
from .records import create
from .image_options import options


def schema(caps):
    from .tool_schema import tool, field
    return tool("image_settings", "Choose an available SDXL model and sampling options for subsequent queued jobs.",
        {"checkpoint": field("string", enum=caps["checkpoints"]),
         "sampler_name": field("string", enum=caps["enums"]["sampler_name"]),
         "scheduler": field("string", enum=caps["enums"]["scheduler"])})


def select(e, sid, args):
    if set(args) - {"checkpoint", "sampler_name", "scheduler"}:
        raise ValueError("Unknown model setting")
    current = e.db.session(sid)["settings"]
    values = options(e.caps, current, args)
    current.update({k: values[k] for k in args})
    e.db.sql("UPDATE sessions SET settings=? WHERE id=?", (json.dumps(current), sid))
    return create(e.db, sid, "result", {"settings": {k: values[k] for k in args}})
