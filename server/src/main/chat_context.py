import json
from .records import flat
from .tool_schema import schemas


def brief(result):
    if result.get("kind") == "job":
        return {k: result[k] for k in ("id", "status", "mode")}
    if "jobs" in result and isinstance(result["jobs"], list):
        result = dict(result)
        result["jobs"] = [{k: j[k] for k in ("id", "mode", "status") if k in j}
                          if isinstance(j, dict) else j for j in result["jobs"]]
    return result


def build(e, sid, ident, messages):
    jobs = [j for j in flat(e.db, sid, "job") if j["id"] > ident]
    inventory = [{k: j[k] for k in ("id", "status", "mode", "image") if k in j} for j in jobs]
    images = [{"image": i["id"], "operation": i["operation"]} for i in flat(e.db, sid, "image") if not i.get("deleted")]
    note = "Current images: " + json.dumps(images) + "\nExisting work; do not repeat: " + json.dumps(inventory)
    if jobs and all(j["status"] == "done" for j in jobs):
        note += "\nThe batch is complete. Inspect the attached results and answer."
    return messages + [{"role": "user", "content": "Workbench state (reference data):\n" + note}], schemas(e.caps)
