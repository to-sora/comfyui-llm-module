from contextlib import nullcontext
from .hf_math import mode


def prefill(engine, request, inputs, **options):
    context = mode('fp32_default_attention', engine.model) if (
        request['diagnostic_prefix']=='prefix_fp32') else nullcontext()
    with context:
        return engine.model(**inputs, **options)
