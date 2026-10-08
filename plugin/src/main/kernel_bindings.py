"""Describe locally resolved hybrid kernels without importing another model."""
import inspect
import sys


def describe(model):
    module = sys.modules.get(type(model).__module__)
    result = {}
    for name in ('causal_conv1d_fn', 'causal_conv1d_update',
                 'torch_chunk_gated_delta_rule', 'torch_recurrent_gated_delta_rule'):
        function = getattr(module, name, None)
        if function is None:
            continue
        result[name] = {'implementation': function.__module__+'.'+function.__name__,
                        'external': False if not hasattr(function, '__wrapped__')
                        and function.__module__.startswith('transformers.') else None}
        for _ in range(8):
            cells = inspect.getclosurevars(function).nonlocals if inspect.isfunction(function) else {}
            if 'implementation' in cells:
                target = cells['implementation']
                result[name] = {'implementation': target.__module__+'.'+target.__name__,
                                'external': cells.get('is_new_implementation')}
                break
            function = getattr(function, '__wrapped__', None)
            if function is None:
                break
    return result
