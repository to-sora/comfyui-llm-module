class UserError(ValueError):
    """Invalid client input distinguished from inference and programming errors."""


def message(exc):
    return str(exc).strip() or f"{type(exc).__name__}: inference did not complete."


async def json_body(request):
    from json import JSONDecodeError
    try:
        return await request.json()
    except (JSONDecodeError, UnicodeDecodeError) as exc:
        raise UserError("The request contains invalid JSON") from exc
