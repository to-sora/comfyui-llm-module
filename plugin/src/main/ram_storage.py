"""Detach CPU weights from file mappings without duplicating tied storages."""
from bisect import bisect_right
from pathlib import Path
import torch
from .residency import tensors


def materialize(model):
    ranges=[]
    for line in Path('/proc/self/maps').read_text().splitlines():
        fields=line.split(maxsplit=5)
        if len(fields)==6 and fields[5].split(' (deleted)')[0].endswith(('.safetensors','.bin','.gguf','.pt')):
            first,last=fields[0].split('-')
            ranges.append((int(first,16),int(last,16)))
    ranges.sort()
    starts=[first for first,_ in ranges]
    copies={}
    for tensor in tensors(model):
        if tensor.device.type!='cpu':
            continue
        storage=tensor.untyped_storage()
        pointer=storage.data_ptr()
        index=bisect_right(starts,pointer)-1
        if index<0 or pointer>=ranges[index][1]:
            continue
        key=(pointer,storage.nbytes())
        if key not in copies:
            view=torch.empty(0,dtype=torch.uint8).set_(storage,0,(storage.nbytes(),),(1,))
            copies[key]=view.clone().untyped_storage()
        tensor.data=torch.empty(0,dtype=tensor.dtype).set_(copies[key],tensor.storage_offset(),
                                                         tensor.size(),tensor.stride())
