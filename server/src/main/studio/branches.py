from ..errors import UserError


def idle(e, chat):
    if e.db.one("SELECT id FROM runs WHERE chat_id=? AND status IN ('queued','running')",(chat,)):
        raise UserError('Stop this reply before changing versions')


def chain(db, chat):
    tip = db.get('chats',chat)['tip']
    return db.all('''WITH RECURSIVE branch AS (
        SELECT * FROM messages WHERE id=? AND chat_id=? UNION ALL
        SELECT m.* FROM messages m JOIN branch b ON m.id=b.parent_id WHERE m.chat_id=?)
        SELECT * FROM branch ORDER BY id''',(tip,chat,chat))


def select(e, chat, ident):
    idle(e,chat)
    row = e.db.get('messages',ident)
    if row['chat_id'] != chat:
        raise UserError('Choose a version from this chat')
    while child := e.db.one('SELECT id FROM messages WHERE chat_id=? AND parent_id=? ORDER BY id DESC LIMIT 1',(chat,ident)):
        ident = child['id']
    e.db.update('chats',chat,tip=ident,summary='',summary_through='')
    e.events.publish(chat,'branch.changed',{'tip':ident})


def versions(db, row):
    return db.all('SELECT id FROM messages WHERE chat_id=? AND parent_id IS ? AND role=? ORDER BY id',
                  (row['chat_id'],row['parent_id'],row['role']))
