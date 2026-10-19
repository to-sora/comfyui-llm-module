"""Admission before allocation; reservations include the eventual CPU copy."""
import threading
import psutil
from . import ram_cleanup

GB = 1024**3
LIMIT, FLOOR, HEADROOM, LLM_LIMIT = 80_000_000_000, 8*GB, 20*GB, 35_000_000_000
LOCK = threading.RLock()
RESERVATIONS = {}
TRACKERS = {}


def available():
    v = psutil.virtual_memory()
    return min(v.available, max(0, LIMIT-(v.total-v.available)))


def check(extra=0, returning=0, floor=HEADROOM):
    free = available()
    if free < extra+returning+floor:
        ram_cleanup.reclaim()
        free = available()
    if free < extra+returning+floor:
        raise MemoryError(f'RAM admission refused: {free/GB:.1f} GiB available within '
                          f'the 80 GB plan; {(extra+returning+floor)/GB:.1f} GiB required. '
                          'Existing weights remain in RAM; no disk reload is attempted.')


def reserve(key, size, transient=0, kind='llm'):
    with LOCK:
        if key in RESERVATIONS:
            return
        used = sum(v['bytes'] for v in RESERVATIONS.values() if v['kind']==kind)
        limit = {'llm':LLM_LIMIT,'sdxl':14_000_000_000,'aux':1_000_000_000}[kind]
        if used+size > limit:
            raise MemoryError(f'{kind} resident budget exceeded: '
                              f'{(used+size)/GB:.1f} GiB requested, {limit/GB:.0f} GiB limit')
        check(size+transient, returning())
        entry = {'bytes':size, 'kind':kind, 'gpu':0, 'state':'admitted'}
        RESERVATIONS[key] = entry
        return entry


def release(key, token):
    with LOCK:
        if token is not None and RESERVATIONS.get(key) is token:
            TRACKERS.pop(key, None)
            del RESERVATIONS[key]


def returning():
    with LOCK:
        for key,track in TRACKERS.items():
            RESERVATIONS[key]['gpu']=int(track())
        return sum(v['gpu'] for v in RESERVATIONS.values())


def update(key, size, gpu=0):
    with LOCK:
        entry = RESERVATIONS[key]
        entry.update(bytes=max(entry['bytes'],size), gpu=gpu, state='resident')


def snapshot():
    returning()
    return {'planning_bytes':LIMIT, 'available_bytes':available(), 'floor_bytes':FLOOR,
            'target_headroom_bytes':HEADROOM, 'llm_limit_bytes':LLM_LIMIT,
            'unused_cpu_cleanup':ram_cleanup.snapshot(),
            'reservations':{str(k):dict(v) for k,v in RESERVATIONS.items()}}
