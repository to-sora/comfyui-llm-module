"""Process-lifetime ledger, including failed reads and conversion attempts."""
from pathlib import Path
from .ram_budget import LOCK

READS = {}


def identity(source):
    path = Path(source)
    return str(path.resolve()) if path.exists() else source


def claim(source, purpose):
    key = identity(source)
    with LOCK:
        if key in READS:
            raise RuntimeError('R2: these weights were already read during this process: '+key+
                               '. Reuse the resident representation; another read is refused.')
        READS[key] = {'purpose':purpose, 'reads':1, 'state':'reading'}
    return key


def completed(source):
    READS[identity(source)]['state'] = 'resident'


def staging_bytes(source):
    path = Path(source)
    sizes = [p.stat().st_size for p in path.glob('*.safetensors')] if path.is_dir() else []
    return max(sizes or [4*1024**3]) + 2*1024**3
