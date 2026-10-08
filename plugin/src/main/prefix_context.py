from contextlib import contextmanager, nullcontext
from .prefix_cache import boundary, cached
from .hf_math import mode


def supported(cfg, model_type):
    return (model_type == 'qwen3_5' and cfg['quantization'] == 'bnb_nf4'
            and cfg['kv_quantization'] == 'hqq_8' and cfg.get('precision','bfloat16') == 'bfloat16')


def workspace(cfg, config, tokens):
    if not supported(cfg, config.get('model_type')):
        return 0
    text = config.get('text_config', config)
    hidden, width = text['hidden_size'], text['intermediate_size']
    return 4*(width*hidden + tokens*(width+hidden))


@contextmanager
def prepared(engine, request, inputs):
    config = engine.model.config
    hybrid = 'linear_attention' in getattr(config.get_text_config(),'layer_types',[])
    vision = any(key.startswith('pixel_values') for key in inputs)
    eligible = supported(engine.cfg, config.model_type) and engine.model.device.type == 'cuda'
    bypass = 'hybrid_vision_full_prefill' if hybrid and vision and not eligible else None
    ids = boundary(engine,request,inputs) if request.get('prefix_cache',True) and not bypass else ()
    policy = 'mlp_down_fp32' if ids and hybrid and vision else 'default'
    with mode(policy,engine.model) if policy != 'default' else nullcontext():
        yield cached(engine,inputs,ids,policy,bypass)
