from collections import OrderedDict
from copy import copy


def snapshot(value, device, memo=None):
    import torch
    memo = {} if memo is None else memo
    if id(value) in memo:
        return memo[id(value)]
    if isinstance(value, torch.Tensor):
        result = value.detach().to(device=device, copy=True)
    elif isinstance(value, torch.device):
        result = torch.device(device)
    elif isinstance(value, dict):
        result = {k: snapshot(v, device, memo) for k, v in value.items()}
    elif isinstance(value, (tuple, list)):
        result = type(value)(snapshot(v, device, memo) for v in value)
    elif hasattr(value, "__dict__") and not isinstance(value, type):
        result = copy(value)
        memo[id(value)] = result
        for key, item in vars(value).items():
            setattr(result, key, snapshot(item, device, memo))
    else:
        result = value
    memo[id(value)] = result
    return result


def nbytes(value, seen=None):
    seen = set() if seen is None else seen
    if id(value) in seen:
        return 0
    seen.add(id(value))
    if hasattr(value, "numel") and hasattr(value, "element_size"):
        return value.numel() * value.element_size()
    if isinstance(value, (bytes, bytearray)):
        return len(value)
    if isinstance(value, dict):
        return sum(nbytes(v, seen) for v in value.values())
    if isinstance(value, (list, tuple)):
        return sum(nbytes(v, seen) for v in value)
    if hasattr(value, "__dict__"):
        return nbytes(vars(value), seen)
    return 0


class PrefixCache:
    def __init__(self, budget):
        self.budget = budget
        self.entries = OrderedDict()
        self.bytes = self.hits = 0

    def put(self, tokens, state, size):
        key = tuple(tokens)
        if size > self.budget or not key:
            return False
        old = self.entries.pop(key, None)
        self.bytes -= old[1] if old else 0
        while self.entries and self.bytes + size > self.budget:
            _, (_, removed) = self.entries.popitem(last=False)
            self.bytes -= removed
        self.entries[key] = state, size
        self.bytes += size
        return True

    def match(self, tokens):
        keys = [k for k in self.entries if len(k) < len(tokens)
                and tuple(tokens[:len(k)]) == k]
        if not keys:
            return None
        key = max(keys, key=len)
        self.entries.move_to_end(key)
        self.hits += 1
        return self.entries[key][0]
