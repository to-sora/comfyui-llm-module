from plugin.src.main.cache import PrefixCache
from plugin.src.main.pool import Pool


class Engine:
    def __init__(self, cfg):
        self.closed = False
        self.cache = PrefixCache(32)

    def warm(self):
        self.cache.put([11, 22], b"state", 5)

    def close(self):
        self.closed = True


def pool(workers=2):
    return Pool({"workers": workers, "queue_limit": 4, "queue_timeout": 2}, Engine)
