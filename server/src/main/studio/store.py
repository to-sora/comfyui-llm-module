import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from ..settings import DATA
from ..errors import UserError


def encode(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'))


def unpack(row):
    if row is None:
        return None
    return {(key[:-5] if key.endswith('_json') else key):
            json.loads(value) if key.endswith('_json') else value for key, value in dict(row).items()}


class Store:
    def __init__(self):
        self.db = sqlite3.connect(DATA / 'studio.sqlite', isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.executescript(Path(__file__).with_name('schema.sql').read_text())

    @contextmanager
    def transaction(self):
        nested = self.db.in_transaction
        if not nested:
            self.db.execute('BEGIN IMMEDIATE')
        try:
            yield
            if not nested:
                self.db.commit()
        except BaseException:
            if not nested:
                self.db.rollback()
            raise

    def all(self, sql, args=()):
        return [unpack(r) for r in self.db.execute(sql, args)]

    def one(self, sql, args=()):
        return unpack(self.db.execute(sql, args).fetchone())

    def get(self, table, ident):
        if table not in ('chats', 'messages', 'runs', 'images'):
            raise RuntimeError('Unknown record table')
        value = self.one(f'SELECT * FROM {table} WHERE id=?', (ident,))
        if value is None:
            raise UserError('The requested item no longer exists')
        return value

    def insert(self, table, **values):
        fields = ','.join(values)
        self.db.execute(f'INSERT INTO {table}({fields}) VALUES({",".join("?" for _ in values)})',
                        tuple(values.values()))
        return values.get('id')

    def update(self, table, ident, **values):
        self.db.execute(f'UPDATE {table} SET {",".join(k+"=?" for k in values)} WHERE id=?',
                        (*values.values(), ident))
        return self.get(table, ident)

    def reference(self, chat, image, number=None):
        found = self.one('SELECT number FROM image_refs WHERE chat_id=? AND image_id=?', (chat, image))
        if found:
            return found['number']
        if number is None:
            number = self.one('SELECT COALESCE(MAX(number),0)+1 AS n FROM image_refs WHERE chat_id=?', (chat,))['n']
        self.insert('image_refs', chat_id=chat, image_id=image, number=number)
        return number
