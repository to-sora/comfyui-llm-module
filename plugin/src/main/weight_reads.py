"""Process-lifetime ledger, including failed reads and conversion attempts."""
from pathlib import Path
from .ram_budget import LOCK

READS = {}
REPRESENTATIONS = {}


def identity(source):
    path = Path(source)
    return str(path.resolve()) if path.exists() else source


def claim(source, purpose, representation=None):
    key = identity(source)
    with LOCK:
        if key in READS or (representation is not None and representation in REPRESENTATIONS):
            raise RuntimeError('R2: these weights were already read during this process: '+key+
                               '. Reuse the resident representation; another read is refused.')
        READS[key] = {'purpose':purpose, 'reads':1, 'state':'reading'}
        if representation is not None:
            REPRESENTATIONS[representation] = key
    return key


def completed(source):
    READS[identity(source)]['state'] = 'resident'


def failed_since(before, error):
    with LOCK:
        for key in READS.keys()-before:
            READS[key].update(state='failed', error=type(error).__name__)


def staging_bytes(source):
    path = Path(source)
    sizes = [p.stat().st_size for p in path.glob('*.safetensors')] if path.is_dir() else []
    return max(sizes or [4*1024**3]) + 2*1024**3
