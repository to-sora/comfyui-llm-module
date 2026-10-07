from .errors import UserError
import json
import time


def create(db, sid, kind, data):
    row = db.sql("SELECT COALESCE(MAX(id),-1)+1 FROM records WHERE session=?", (sid,)).fetchone()
    ident = row[0]
    if ident > 10000:
        raise UserError("This session has used all native IDs. Create another session.")
    db.sql("INSERT INTO records VALUES(?,?,?,?,?)", (sid, ident, kind, json.dumps(data), time.time()))
    return {"id": ident, "kind": kind, **data}


def get(db, sid, ident, kind=None):
    if type(ident) is not int or not 0 <= ident <= 20000:
        raise UserError("Expected a session integer ID (0–20000)")
    if ident > 10000:
        from .sharing import resolve
        result = resolve(db, sid, ident)
    else:
        row = db.sql("SELECT * FROM records WHERE session=? AND id=?", (sid, ident)).fetchone()
        if not row:
            raise UserError("ID not found in this session")
        result = {"id": ident, "kind": row["kind"], **json.loads(row["data"])}
    if result.get("deleted"):
        raise UserError("This item was deleted")
    if kind and result["kind"] != kind:
        raise UserError(f"Expected {kind}, found {result['kind']}")
    return result


def update(db, sid, ident, **changes):
    if ident > 10000:
        raise UserError("Shared IDs are read-only")
    value = get(db, sid, ident)
    kind = value.pop("kind")
    value.pop("id")
    value.update(changes)
    db.sql("UPDATE records SET data=? WHERE session=? AND id=?", (json.dumps(value), sid, ident))
    return {"id": ident, "kind": kind, **value}


def flat(db, sid, kind=None):
    return [{"id": r["id"], "kind": r["kind"], **r["data"]} for r in db.records(sid, kind)]
