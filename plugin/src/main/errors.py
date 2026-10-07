class UserError(ValueError):
    """Invalid client input distinguished from inference and programming errors."""


def message(exc):
    return str(exc).strip() or f"{type(exc).__name__}: inference did not complete."
