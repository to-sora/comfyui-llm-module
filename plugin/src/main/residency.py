import torch


def sizes(model):
    seen = set()
    maps = set()
    totals = {"cpu": 0, "cuda": 0}
    def count(value):
        if isinstance(value, torch.Tensor) and value.device.type != "meta":
            store = value.untyped_storage()
            key = (str(value.device), store.data_ptr())
            if key not in seen:
                seen.add(key)
                totals[value.device.type] = totals.get(value.device.type, 0) + store.nbytes()
        elif isinstance(value, dict):
            for v in value.values(): count(v)
        elif isinstance(value, (tuple, list)):
            for v in value: count(v)
    for param in list(model.parameters()) + list(model.buffers()):
        count(param)
        state = getattr(param, "quant_state", None)
        while state is not None:
            for name in ("absmax", "code", "offset"):
                count(getattr(state, name, None))
            state = getattr(state, "state2", None)
        for name in ("SCB", "CB"):
            count(getattr(param, name, None))
    def hook_storage(hook):
        dataset = getattr(hook, "weights_map", None)
        while hasattr(dataset, "dataset"):
            dataset = dataset.dataset
        if dataset is not None and id(dataset) not in maps:
            maps.add(id(dataset))
            count(getattr(dataset, "state_dict", dataset))
        for child in getattr(hook, "hooks", []):
            hook_storage(child)
    for module in model.modules():
        hook_storage(getattr(module, "_hf_hook", None))
        state = getattr(module, "state", None)
        for name in ("SCB", "CB", "CxB"):
            count(getattr(state, name, None))
    return totals
