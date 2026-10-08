import copy
import torch
from transformers.cache_utils import HQQQuantizedLayer
from .kv_cache import create, QuantizedSlidingLayer


def clone(cache, device):
    def move(value):
        if isinstance(value, torch.Tensor):
            return value.detach().to(device, copy=True)
        if isinstance(value, torch.device):
            return torch.device(device)
        if isinstance(value, dict):
            return {k:move(v) for k,v in value.items()}
        if isinstance(value, (list,tuple)):
            return type(value)(move(v) for v in value)
        return value
    result = copy.copy(cache)
    result.layers = []
    for source in cache.layers:
        layer = copy.copy(source)
        layer.__dict__ = {k:move(v) for k,v in vars(source).items()}
        result.layers.append(layer)
    return result


class PrefixJoin:
    def update(self, keys, values, *args, **kwargs):
        if hasattr(self, 'prefix'):
            previous = self.cumulative_length
            added = keys.shape[-2]
            old_keys, old_values = self.prefix
            del self.prefix
            self.cumulative_length = 0
            result = super().update(torch.cat([old_keys,keys],dim=-2),
                                    torch.cat([old_values,values],dim=-2),*args,**kwargs)
            self.cumulative_length = previous + added
            return result
        return super().update(keys, values, *args, **kwargs)


class JoinedQuantized(PrefixJoin, HQQQuantizedLayer):
    pass


class JoinedSliding(PrefixJoin, QuantizedSlidingLayer):
    pass


def restore(snapshot, config, mode, device):
    saved = clone(snapshot, device)
    if mode == 'none':
        return saved
    result = create(config, mode)
    for index, old in enumerate(saved.layers):
        layer = result.layers[index]
        if isinstance(layer, HQQQuantizedLayer):
            cls = JoinedSliding if isinstance(layer, QuantizedSlidingLayer) else JoinedQuantized
            joined = cls.__new__(cls)
            joined.__dict__ = vars(layer).copy()
            result.layers[index] = layer = joined
            layer.prefix = old.keys, old.values
            layer.cumulative_length = old.get_seq_length()
        else:
            result.layers[index] = old
    return result


def tensors(cache):
    def walk(value):
        if isinstance(value, torch.Tensor):
            yield value
        elif isinstance(value, dict):
            for item in value.values():
                yield from walk(item)
    for layer in cache.layers:
        yield from walk(vars(layer))
