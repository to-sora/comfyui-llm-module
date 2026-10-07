import logging
from logging.handlers import RotatingFileHandler
from .settings import APP


def install():
    handler = RotatingFileHandler(APP / "data/service.log", maxBytes=10*1024**2, backupCount=4)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logging.getLogger().addHandler(handler)
