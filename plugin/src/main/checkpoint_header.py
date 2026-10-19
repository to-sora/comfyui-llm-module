"""Validate safetensors metadata and file bounds without reading weights."""
import json
import struct
from pathlib import Path


def shapes(path):
    path=Path(path)
    if path.suffix!='.safetensors':
        raise ValueError('Use a safetensors checkpoint for metadata-only discovery')
    with path.open('rb') as stream:
        size=struct.unpack('<Q',stream.read(8))[0]
        if not 2<=size<=32*1024*1024:
            raise ValueError('Invalid tensor header')
        header=json.loads(stream.read(size))
    tensors={k:v for k,v in header.items() if k!='__metadata__'}
    ranges=sorted(v['data_offsets'] for v in tensors.values())
    end=0
    for start,stop in ranges:
        if type(start) is not int or type(stop) is not int or start!=end or stop<start:
            raise ValueError('Invalid tensor file ranges')
        end=stop
    if size+8+end!=path.stat().st_size:
        raise ValueError('Incomplete checkpoint: file size differs from tensor metadata')
    return {k:v['shape'] for k,v in tensors.items()}
