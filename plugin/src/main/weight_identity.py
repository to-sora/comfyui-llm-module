"""Stable origin across locally generated NF4 cache paths."""
from pathlib import Path
from .settings import APP
from .weight_reads import identity


def origin(source):
    value = identity(source)
    cache = (APP/'data/quantized').resolve()
    seen = set()
    while Path(value).is_relative_to(cache):
        marker = Path(value)/'source.txt'
        if not marker.is_file():
            break
        if value in seen:
            raise ValueError('Cyclic quantized-cache source markers')
        seen.add(value)
        value = identity(marker.read_text().strip())
    return value


def representation(cfg):
    return (origin(cfg['model']), cfg['quantization'])
