import torch
from transformers import DynamicCache
from transformers.cache_utils import DynamicLayer, DynamicSlidingWindowLayer, HQQQuantizedLayer


class QuantizedSlidingLayer(HQQQuantizedLayer):
    is_sliding = True

    def __init__(self, window, nbits):
        super().__init__(nbits=nbits, axis_key=1, axis_value=1, q_group_size=64)
        self.sliding_window = window

    def update(self, keys, values, *args, **kwargs):
        if not self.is_initialized:
            self.lazy_initialization(keys, values)
            full_keys, full_values = keys, values
        else:
            full_keys = torch.cat([self._dequantize(self._quantized_keys), keys], dim=-2)
            full_values = torch.cat([self._dequantize(self._quantized_values), values], dim=-2)
        self.cumulative_length += keys.shape[-2]
        retained = slice(-self.sliding_window + 1, None)
        self._quantized_keys = self._quantize(full_keys[:, :, retained, :].contiguous(), 1)
        self._quantized_values = self._quantize(full_values[:, :, retained, :].contiguous(), 1)
        return full_keys, full_values

    get_mask_sizes = DynamicSlidingWindowLayer.get_mask_sizes

    def get_max_length(self):
        return self.sliding_window


def create(config, mode):
    cache = DynamicCache(config=config)
    if mode == "none":
        return cache
    if mode not in {"hqq_4", "hqq_8"}:
        raise ValueError("HF KV quantization: none, hqq_4, hqq_8")
    bits = int(mode.split("_")[1])
    for i, layer in enumerate(cache.layers):
        if isinstance(layer, DynamicSlidingWindowLayer):
            cache.layers[i] = QuantizedSlidingLayer(layer.sliding_window, bits)
        elif type(layer) is DynamicLayer:
            cache.layers[i] = HQQQuantizedLayer(
                nbits=bits, axis_key=1, axis_value=1, q_group_size=64,
                residual_length=32)
    return cache
