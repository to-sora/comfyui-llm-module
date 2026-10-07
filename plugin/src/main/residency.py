import torch


def sizes(model):
    seen = set()
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
        if state:
            count(state.as_dict())
        for name in ("SCB", "CB"):
            count(getattr(param, name, None))
    return totals
