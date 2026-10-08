"""Measure request allocation inside ComfyUI's serialized model execution."""
from contextlib import contextmanager
import torch


@contextmanager
def measured(engine, required):
    device = engine.model.device
    if device.type != 'cuda':
        yield
        return
    initial = torch.cuda.memory_allocated(device)
    torch.cuda.reset_peak_memory_stats(device)
    try:
        yield
    finally:
        peak = torch.cuda.max_memory_allocated(device)
        engine.diagnostics['working_memory'] = {
            'reserved_working_bytes': required,
            'initial_allocated_bytes': initial,
            'peak_allocated_bytes': peak,
            'peak_extra_bytes': max(0, peak-initial),
            'final_allocated_bytes': torch.cuda.memory_allocated(device)}
