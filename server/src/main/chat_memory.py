import json
from .records import flat
from .sharing import available


def summary(e, sid):
    turns = [c for c in flat(e.db, sid, "chat") if c["status"] == "done"]
    recent = ""
    if turns:
        last = turns[-1]
        recent = "Previous turn: " + json.dumps({"user": last["text"][:250],
            "assistant": (last.get("response") or "")[:350]})
    images = [i for i in flat(e.db, sid, "image") if not i.get("deleted") and i["operation"] != "mask"]
    images += available(e.db, sid)
    inventory = [{"id": i["id"], "operation": i["operation"]} for i in images[-8:]]
    return recent + "\nAvailable image IDs (use view_images to see pixels): " + json.dumps(inventory)
