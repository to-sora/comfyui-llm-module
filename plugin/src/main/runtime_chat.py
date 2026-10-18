from comfy import model_management as mm
from .estimate import working
from . import ram_budget


def chat(owner, request, images, cfg):
    owner.cfg = dict(cfg)
    ram_budget.check(256*1024**2, ram_budget.returning())
    owner.ensure_engine()
    owner.engine.cfg = owner.cfg
    ram_budget.check(256*1024**2, ram_budget.returning())
    inputs = owner.engine.prepare(request, images)
    length = inputs['input_ids'].shape[-1] + request.get('max_completion_tokens', request.get('max_tokens',256))
    if length > cfg['context_tokens']:
        raise ValueError('Prompt and reply exceed context capacity')
    pixels = sum(v.numel() for k,v in inputs.items() if k.startswith('pixel_values'))
    required = working(cfg,length,pixels,request.get('diagnostic_prefix'))
    # Prefix snapshots and CPU inference are admitted in addition to weights.
    ram_budget.check(required, ram_budget.returning())
    mm.load_models_gpu([owner.patcher], memory_required=required)
    mm.throw_exception_if_processing_interrupted()
    return owner.engine.chat(request,inputs,required)
