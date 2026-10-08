PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS chats(
 id TEXT PRIMARY KEY,title TEXT,created REAL,updated REAL,pinned INTEGER DEFAULT 0,
 archived INTEGER DEFAULT 0,summary TEXT DEFAULT '',summary_through TEXT DEFAULT '',
 tip TEXT,settings_json TEXT DEFAULT '{}');
CREATE TABLE IF NOT EXISTS messages(
 id TEXT PRIMARY KEY,chat_id TEXT REFERENCES chats(id),parent_id TEXT,role TEXT,
 parts_json TEXT,created REAL,run_id TEXT);
CREATE INDEX IF NOT EXISTS messages_chat ON messages(chat_id,id);
CREATE TABLE IF NOT EXISTS runs(
 id TEXT PRIMARY KEY,chat_id TEXT REFERENCES chats(id),message_id TEXT,assistant_id TEXT,
 status TEXT,trace_json TEXT DEFAULT '{}',settings_json TEXT,created REAL,
 started REAL,finished REAL,error TEXT,cancelled INTEGER DEFAULT 0);
CREATE INDEX IF NOT EXISTS runs_chat ON runs(chat_id,id);
CREATE INDEX IF NOT EXISTS runs_queue ON runs(status,id);
CREATE TABLE IF NOT EXISTS images(
 id TEXT PRIMARY KEY,sha256 TEXT,file TEXT,width INTEGER,height INTEGER,
 parents_json TEXT,recipe_json TEXT,chat_id TEXT REFERENCES chats(id),message_id TEXT,
 favorite INTEGER DEFAULT 0,created REAL,thumb TEXT,bytes INTEGER,deleted INTEGER DEFAULT 0,
 kind TEXT DEFAULT 'upload');
CREATE INDEX IF NOT EXISTS images_chat ON images(chat_id,id);
CREATE INDEX IF NOT EXISTS images_library ON images(deleted,kind,id);
CREATE TABLE IF NOT EXISTS image_refs(
 chat_id TEXT REFERENCES chats(id),image_id TEXT REFERENCES images(id),number INTEGER,
 PRIMARY KEY(chat_id,image_id),UNIQUE(chat_id,number));
CREATE TABLE IF NOT EXISTS events(
 seq INTEGER PRIMARY KEY AUTOINCREMENT,chat_id TEXT,kind TEXT,data_json TEXT,created REAL);
CREATE INDEX IF NOT EXISTS events_chat ON events(chat_id,seq);
CREATE INDEX IF NOT EXISTS events_global ON events(kind,seq);
CREATE TABLE IF NOT EXISTS preferences(key TEXT PRIMARY KEY,value_json TEXT);
CREATE TABLE IF NOT EXISTS legacy(
 kind TEXT,session TEXT,number INTEGER,id TEXT,PRIMARY KEY(kind,session,number));
