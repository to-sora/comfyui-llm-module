import torch
import psutil
from accelerate import dispatch_model, infer_auto_device_map
from accelerate.hooks import remove_hook_from_module
from .offload_budget import weight_budget
from .int8_move import move_state


def placement(model, device, budget):
    if device == "cpu":
        return {"": "cpu"}
    return infer_auto_device_map(model, max_memory={torch.device(device).index or 0: weight_budget(model.config, budget),
        "cpu": int(psutil.virtual_memory().available * .85)},
        no_split_module_classes=getattr(model, "_no_split_modules", []))


def move(model, device, budget):
    remove_hook_from_module(model, recurse=True)
    if device == "cpu" or model.get_memory_footprint() <= budget:
        move_state(model, device)
        model.to(device)
        model.hf_device_map = {"": device}
    else:
        move_state(model, "cpu")
        mapping = placement(model, device, budget)
        if "disk" in mapping.values():
            raise MemoryError("The model needs more system RAM; disk offload is disabled")
        dispatch_model(model, device_map=mapping)
        model.hf_device_map = mapping
    return model
