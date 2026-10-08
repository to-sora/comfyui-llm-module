from contextlib import contextmanager
import torch.nn.functional as functional
from bitsandbytes.functional import dequantize_4bit


@contextmanager
def dense_prefill(model):
    saved = []
    try:
        for module in model.modules():
            if type(module).__name__!='Linear4bit':
                continue
            original = module.forward
            saved.append((module, 'forward' in module.__dict__, original))

            def forward(value, layer=module, fallback=original):
                if value.device.type!='cuda' or value.numel()==value.shape[-1]:
                    return fallback(value)
                dtype = layer.compute_dtype or value.dtype
                weight = dequantize_4bit(layer.weight.data, layer.weight.quant_state).to(dtype)
                bias = layer.bias.to(dtype) if layer.bias is not None else None
                return functional.linear(value.to(dtype), weight, bias).to(value.dtype)

            module.forward = forward
        yield
    finally:
        for module,owned,original in saved:
            if owned:
                module.forward = original
            else:
                del module.forward
