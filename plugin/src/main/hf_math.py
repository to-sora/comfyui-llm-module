from contextlib import contextmanager, nullcontext
import torch
from torch.nn.attention import sdpa_kernel, SDPBackend
from .prefix_probe_linear import dense_prefill
from .hf_precision import precision


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
        'default','full_accumulation','fp32_default_attention','prefill_fp32','dense_prefill',
        'attention_fp32','mlp_fp32','head_fp32','mlp_down_fp32','mlp_gateup_fp32','prefill_fp16') else nullcontext()
    try:
        if name != 'default':
            for key in names:
                setattr(backend,key,False)
        if name == 'fixed_reduction':
            torch.backends.cuda.preferred_blas_library('cublaslt')
            for key in names[1:]:
                setattr(backend,key,(False,False))
        with attention, precision(model, name), dense_prefill(model) if name=='dense_prefill' else nullcontext():
            yield
    finally:
        for key,value in original.items():
            setattr(backend,key,value)
        torch.backends.cuda.preferred_blas_library(library)
