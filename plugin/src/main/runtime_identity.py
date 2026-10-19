import torch
from comfy import model_management as mm
from .weight_identity import representation


def canonical(cfg):
    requested = cfg.get('device', 'auto')
    device = torch.device(mm.get_torch_device() if requested == 'auto' else requested)
    if device.type == 'cuda' and device.index is None:
        device = torch.device('cuda', torch.cuda.current_device())
    value = {**cfg, 'device':str(device)}
    key = (*representation(value), value.get('precision','bfloat16'), value['device'])
    return value, key
