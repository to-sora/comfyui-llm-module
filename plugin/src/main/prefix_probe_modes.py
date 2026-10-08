from contextlib import contextmanager, nullcontext
import torch
from torch.nn.attention import sdpa_kernel, SDPBackend


@contextmanager
def mode(name):
    names = ('allow_tf32','allow_fp16_reduced_precision_reduction','allow_bf16_reduced_precision_reduction')
    backend = torch.backends.cuda.matmul
    original = {key:getattr(backend,key) for key in names}
    for key in names[1:]:
        original[key] = original[key],getattr(backend,key+'_split_k')
    library = torch.backends.cuda.preferred_blas_library()
    attention = sdpa_kernel(SDPBackend.MATH) if name in ('math_attention','fixed_reduction') else nullcontext()
    try:
        if name != 'default':
            for key in names:
                setattr(backend,key,False)
        if name == 'fixed_reduction':
            torch.backends.cuda.preferred_blas_library('cublaslt')
            for key in names[1:]:
                setattr(backend,key,(False,False))
        with attention:
            yield
    finally:
        for key,value in original.items():
            setattr(backend,key,value)
        torch.backends.cuda.preferred_blas_library(library)
