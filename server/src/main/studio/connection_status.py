def message(engine):
    return 'The image engine is unavailable. Reconnecting…' if engine.error else None
