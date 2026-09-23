import copy


def transfer(value, device, memo=None):
    import torch
    memo = {} if memo is None else memo
    if id(value) in memo:
        return memo[id(value)]
    if isinstance(value, torch.Tensor):
        result = value.detach().to(device, copy=True)
    elif isinstance(value, (list, tuple)):
        result = type(value)(transfer(v, device, memo) for v in value)
    elif isinstance(value, dict):
        result = {k: transfer(v, device, memo) for k, v in value.items()}
    elif hasattr(value, "__dict__") and not isinstance(value, type):
        result = copy.copy(value)
        memo[id(value)] = result
        for k, v in vars(value).items():
            setattr(result, k, transfer(v, device, memo))
    else:
        return value
    memo[id(value)] = result
    return result


def byte_size(value, seen=None):
    import torch
    seen = set() if seen is None else seen
    if id(value) in seen:
        return 0
    seen.add(id(value))
    if isinstance(value, torch.Tensor):
        return value.nelement() * value.element_size()
    if isinstance(value, dict):
        return sum(byte_size(v, seen) for v in value.values())
    if isinstance(value, (list, tuple)):
        return sum(byte_size(v, seen) for v in value)
    if hasattr(value, "__dict__") and not isinstance(value, type):
        return byte_size(vars(value), seen)
    return 0
