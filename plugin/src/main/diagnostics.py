import logging
import threading
from logging.handlers import RotatingFileHandler
from .settings import APP


def install():
    handler = RotatingFileHandler(APP / "data/service.log", maxBytes=10*1024**2, backupCount=4)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logging.getLogger().addHandler(handler)
    previous = threading.excepthook
    def failed(args):
        logging.critical("Worker thread failed: %s", args.thread.name,
                         exc_info=(args.exc_type, args.exc_value, args.exc_traceback))
        previous(args)
    threading.excepthook = failed
