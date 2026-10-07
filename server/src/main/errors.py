class UserError(ValueError):
    """A validated client input error, never an unexpected server exception."""


def message(exc):
    return str(exc).strip() or f"{type(exc).__name__}: the operation did not complete."


def required(data, key):
    if not isinstance(data, dict) or key not in data:
        raise UserError(f"Missing required field: {key}")
    return data[key]
