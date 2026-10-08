from contextlib import contextmanager, nullcontext
import torch
from torch.nn.attention import sdpa_kernel, SDPBackend
from .prefix_probe_linear import dense_prefill


@contextmanager
def mode(name, model):
    if name=='prefix_fp32':
        name='default'
    names = ('allow_tf32','allow_fp16_reduced_precision_reduction','allow_bf16_reduced_precision_reduction')
    backend = torch.backends.cuda.matmul
    original = {key:getattr(backend,key) for key in names}
    for key in names[1:]:
        original[key] = original[key],getattr(backend,key+'_split_k')
    library = torch.backends.cuda.preferred_blas_library()
    attention = sdpa_kernel(SDPBackend.MATH) if name not in (
        'default','full_accumulation','fp32_default_attention','prefill_fp32','dense_prefill') else nullcontext()
    projections = [(m,m.compute_dtype,m.compute_type_is_set,
                    m.bias.dtype if m.bias is not None else None) for m in model.modules()
                   if name in ('fp32_projection','fp32_default_attention','prefill_fp32')
                   and type(m).__name__=='Linear4bit']
    hooks = []
    try:
        for module,dtype,_,_ in projections:
            module.compute_type_is_set = True
            if name=='prefill_fp32':
                def choose(layer, args, original=dtype):
                    value = args[0]
                    layer.compute_dtype = torch.float32 if value.numel()>value.shape[-1] else original
                hooks.append(module.register_forward_pre_hook(choose))
            else:
                module.compute_dtype = torch.float32
        if name != 'default':
            for key in names:
                setattr(backend,key,False)
        if name == 'fixed_reduction':
            torch.backends.cuda.preferred_blas_library('cublaslt')
            for key in names[1:]:
                setattr(backend,key,(False,False))
        with attention, dense_prefill(model) if name=='dense_prefill' else nullcontext():
            yield
    finally:
        for hook in hooks:
            hook.remove()
        for module,dtype,configured,bias_dtype in projections:
            module.compute_dtype, module.compute_type_is_set = dtype, configured
            if bias_dtype is not None:
                module.bias.data = module.bias.data.to(bias_dtype)
        for key,value in original.items():
            setattr(backend,key,value)
        torch.backends.cuda.preferred_blas_library(library)
