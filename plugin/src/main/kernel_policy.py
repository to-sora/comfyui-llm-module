"""Choose hybrid math only inside ComfyUI's serialized inference turn."""
from contextlib import contextmanager
import inspect
import sys
from .kernel_bindings import describe


@contextmanager
def selected(engine, request):
    mode = request.get('diagnostic_kernels', engine.cfg.get('hybrid_kernels', 'reference'))
    if mode not in ('reference', 'local', 'conv', 'delta'):
        raise ValueError('Unknown hybrid kernel mode')
    module = sys.modules.get(type(engine.model).__module__)
    saved = {}
    try:
        for name in ('causal_conv1d_fn', 'causal_conv1d_update',
                     'torch_chunk_gated_delta_rule', 'torch_recurrent_gated_delta_rule'):
            function = getattr(module, name, None)
            if function is None:
                continue
            external = mode == 'local' or (mode == 'conv' and name.startswith('causal_'))
            external |= mode == 'delta' and name.startswith('torch_')
            if not external:
                saved[name] = function
                setattr(module, name, inspect.unwrap(function))
        engine.diagnostics['kernel_mode'] = mode
        engine.diagnostics['hybrid_kernels'] = describe(engine.model)
        yield
    finally:
        for name, function in saved.items():
            setattr(module, name, function)
