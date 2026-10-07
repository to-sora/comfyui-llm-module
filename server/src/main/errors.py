class UserError(ValueError):
    """A validated client input error, never an unexpected server exception."""


def message(exc):
    return str(exc).strip() or f"{type(exc).__name__}: the operation did not complete."


def required(data, key):
    if not isinstance(data, dict) or key not in data:
        raise UserError(f"Missing required field: {key}")
    return data[key]


async def json_body(request):
    from json import JSONDecodeError
    try:
        value = await request.json()
    except (JSONDecodeError, UnicodeDecodeError) as exc:
        raise UserError("The request contains invalid JSON") from exc
    if not isinstance(value, dict):
        raise UserError("The request must be a JSON object")
    return value
