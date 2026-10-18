from ..errors import UserError


def extra(body):
    value={k:bool(body.get(k)) for k in ('safe_images','notifications')}
    for name in ('about_me','reply_instructions'):
        text=body.get(name,'')
        if not isinstance(text,str) or len(text)>4000:
            raise UserError('Custom instructions must be text of at most 4,000 characters per field')
        value[name]=text.strip()
    return value


def instructions(preferences):
    return '\n'.join(label+preferences[key] for key,label in (
        ('about_me','User background and preferences: '),
        ('reply_instructions','User instructions for replies: ')) if preferences.get(key))
