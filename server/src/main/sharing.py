from .records import get, create


def grant(db, sid, ids, enabled):
    for ident in ids:
        if ident > 10000:
            raise ValueError("Only the owner can share or revoke")
        get(db, sid, ident, "image")
    for ident in ids:
        db.sql("INSERT OR REPLACE INTO shares VALUES(?,?,?)", (sid, ident, int(enabled)))
        create(db, sid, "event", {"image": ident, "action": "shared" if enabled else "revoked"})


def resolve(db, sid, ident):
    row = db.sql('''SELECT a.owner,a.target FROM aliases a JOIN shares s
      ON a.owner=s.owner AND a.target=s.target
      WHERE a.session=? AND a.id=? AND s.enabled=1''', (sid, ident)).fetchone()
    if not row:
        raise ValueError("Shared image is unavailable or its sharing was revoked")
    src = get(db, row["owner"], row["target"], "image")
    keep = ("width", "height", "operation", "file", "remote", "thumb", "bytes")
    return {"id": ident, "kind": "image", "readonly": True,
            **{k: src[k] for k in keep if k in src}, "parents": []}


def available(db, sid):
    found = []
    rows = list(db.sql("SELECT * FROM shares WHERE owner!=? AND enabled=1", (sid,)))
    for r in rows:
        alias = db.sql("SELECT id FROM aliases WHERE session=? AND owner=? AND target=?",
                       (sid, r["owner"], r["target"])).fetchone()
        if not alias:
            ident = db.sql("SELECT COALESCE(MAX(id),10000)+1 FROM aliases WHERE session=?", (sid,)).fetchone()[0]
            if ident > 20000:
                raise ValueError("Shared ID range exhausted; create a new session")
            db.sql("INSERT INTO aliases VALUES(?,?,?,?)", (sid, ident, r["owner"], r["target"]))
        else:
            ident = alias[0]
        try:
            found.append(resolve(db, sid, ident))
        except ValueError:
            pass
    return found
