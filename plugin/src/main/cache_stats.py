import math
import torch


def bytes_used(value):
    if isinstance(value, torch.Tensor):
        return value.numel() * value.element_size()
    if isinstance(value, dict):
        return sum(bytes_used(v) for v in value.values())
    if isinstance(value, (list, tuple)):
        return sum(bytes_used(v) for v in value)
    return 0


def describe(cache):
    layers, bits, stored, equivalent = 0, set(), 0, 0
    for layer in cache.layers:
        if not hasattr(layer, "_quantized_keys"):
            continue
        layers += 1
        bits.add(layer.nbits)
        for name in ("keys", "values"):
            quant = getattr(layer, "_quantized_" + name)
            residual = getattr(layer, name)
            stored += bytes_used(quant) + bytes_used(residual)
            equivalent += math.prod(quant[1]["shape"]) * residual.element_size() + bytes_used(residual)
    return {"quantized_layers": layers, "bits": sorted(bits),
            "attention_storage_bytes": stored, "equivalent_float_bytes": equivalent}
