"""Return unused CPU allocations before refusing a retained-model request."""
import ctypes
import gc
import psutil

STATS = {'attempts': 0, 'released_rss_bytes': 0, 'last_released_rss_bytes': 0}


def reclaim():
    process = psutil.Process()
    before = process.memory_info().rss
    gc.collect()
    trim = getattr(ctypes.CDLL(None), 'malloc_trim', None)
    if trim is not None:
        trim.argtypes = [ctypes.c_size_t]
        trim.restype = ctypes.c_int
        trim(0)
    released = max(0, before - process.memory_info().rss)
    STATS['attempts'] += 1
    STATS['released_rss_bytes'] += released
    STATS['last_released_rss_bytes'] = released
    STATS['malloc_trim_available'] = trim is not None


def snapshot():
    return dict(STATS)
