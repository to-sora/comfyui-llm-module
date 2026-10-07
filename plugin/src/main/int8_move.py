import torch
from bitsandbytes.nn import Int8Params, Linear8bitLt


def move_state(model, device):
    """Move packed weights and their non-buffer matmul state together."""
    for layer in model.modules():
        if not isinstance(layer, Linear8bitLt) or layer.weight.dtype != torch.int8:
            continue
        if layer.weight.device.type == "meta":
            continue
        scales = layer.weight.SCB
        if scales is None:
            scales = layer.state.SCB
        if scales is None:
            raise RuntimeError("An INT8 weight is missing its quantization scales")
        data = layer.weight.data.to(device)
        scales = scales.to(device)
        layer.state.reset_grads()
        layer.state.subB = layer.state.idx = None
        layer.weight = Int8Params(data, requires_grad=False, has_fp16_weights=False,
                                 CB=data, SCB=scales)
