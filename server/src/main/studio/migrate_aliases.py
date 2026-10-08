from .migrate import mapped,link


def migrate_aliases(db,old):
    with db.transaction():
        for row in old.execute('SELECT * FROM aliases'):
            image=mapped(db,'image',row['owner'],row['target'])
            if image and not mapped(db,'alias',row['session'],row['id']):
                link(db,'alias',row['session'],row['id'],image)


def notes(db,chat):
    values=db.all('''SELECT a.number AS old,r.number AS current FROM legacy c
        JOIN legacy a ON a.session=c.session AND a.kind='alias'
        JOIN image_refs r ON r.chat_id=c.id AND r.image_id=a.id
        WHERE c.kind='chat' AND c.id=?''',(chat,))
    return '\n'.join(f'Historical image {v["old"]} is now image {v["current"]}.' for v in values)
