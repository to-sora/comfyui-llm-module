from .errors import UserError
import json
import sqlite3
import time
import uuid
from .settings import DATA


class Store:
    def __init__(self):
        self.db = sqlite3.connect(DATA / "workbench.sqlite")
        self.db.row_factory = sqlite3.Row
        self.db.executescript('''PRAGMA journal_mode=WAL;
        CREATE TABLE IF NOT EXISTS sessions(id TEXT PRIMARY KEY,name TEXT,created REAL,settings TEXT);
        CREATE TABLE IF NOT EXISTS records(session TEXT,id INTEGER,kind TEXT,data TEXT,created REAL,
          PRIMARY KEY(session,id));
        CREATE TABLE IF NOT EXISTS shares(owner TEXT,target INTEGER,enabled INTEGER,
          PRIMARY KEY(owner,target));
        CREATE TABLE IF NOT EXISTS aliases(session TEXT,id INTEGER,owner TEXT,target INTEGER,
          PRIMARY KEY(session,id),UNIQUE(session,owner,target));
        CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY,value TEXT);
        ''')

    def sql(self, query, args=()):
        cursor = self.db.execute(query, args)
        self.db.commit()
        return cursor

    def sessions(self):
        return [dict(row) for row in self.sql("SELECT id,name,created FROM sessions ORDER BY created")]

    def session(self, sid):
        row = self.sql("SELECT * FROM sessions WHERE id=?", (sid,)).fetchone()
        if not row:
            raise UserError("Session not found")
        return {**dict(row), "settings": json.loads(row["settings"])}

    def new_session(self, name, settings):
        sid = uuid.uuid4().hex[:12]
        self.sql("INSERT INTO sessions VALUES(?,?,?,?)", (sid, name[:80], time.time(), json.dumps(settings)))
        self.activate(sid)
        return sid

    def activate(self, sid):
        self.session(sid)
        self.sql("INSERT OR REPLACE INTO meta VALUES('active',?)", (sid,))

    def active(self):
        row = self.sql("SELECT value FROM meta WHERE key='active'").fetchone()
        return row[0] if row else None

    def records(self, sid, kind=None):
        query = "SELECT * FROM records WHERE session=?"
        args = (sid,)
        if kind:
            query += " AND kind=?"
            args += (kind,)
        return [self.unpack(r) for r in self.sql(query + " ORDER BY id", args)]

    @staticmethod
    def unpack(row):
        return {**dict(row), "data": json.loads(row["data"])}
