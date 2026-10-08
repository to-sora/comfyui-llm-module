import torch


def tensors(model):
    maps = set()
    def walk(value):
        if isinstance(value, torch.Tensor) and value.device.type != "meta":
            yield value
        elif isinstance(value, dict):
            for item in value.values():
                yield from walk(item)
        elif isinstance(value, (tuple, list)):
            for item in value:
                yield from walk(item)
    for param in list(model.parameters()) + list(model.buffers()):
        yield from walk(param)
        state = getattr(param, "quant_state", None)
        while state is not None:
            for name in ("absmax", "code", "offset"):
                yield from walk(getattr(state, name, None))
            state = getattr(state, "state2", None)
        for name in ("SCB", "CB"):
            yield from walk(getattr(param, name, None))
    def hook_storage(hook):
        dataset = getattr(hook, "weights_map", None)
        while hasattr(dataset, "dataset"):
            dataset = dataset.dataset
        if dataset is not None and id(dataset) not in maps:
            maps.add(id(dataset))
            yield from walk(getattr(dataset, "state_dict", dataset))
        for child in getattr(hook, "hooks", []):
            yield from hook_storage(child)
    for module in model.modules():
        yield from hook_storage(getattr(module, "_hf_hook", None))
        state = getattr(module, "state", None)
        for name in ("SCB", "CB", "CxB"):
            yield from walk(getattr(state, name, None))


def sizes(model):
    seen, totals = set(), {"cpu": 0, "cuda": 0}
    for tensor in tensors(model):
        storage = tensor.untyped_storage()
        key = (str(tensor.device), storage.data_ptr())
        if key not in seen:
            seen.add(key)
            kind = tensor.device.type
            totals[kind] = totals.get(kind, 0) + storage.nbytes()
    return totals
