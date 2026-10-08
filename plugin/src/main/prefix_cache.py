import time
import torch
from .hf_inputs import prepare
from .kv_cache import create
from .prefix_state import clone, restore, tensors


def boundary(engine, request, inputs):
    messages = request['messages']
    if not messages or messages[0]['role'] != 'system' or not isinstance(messages[0].get('content'),str):
        return ()
    static = {**request,'messages':[messages[0],{'role':'user','content':''}]}
    candidate = prepare(engine.processor, engine.vision, static, [])['input_ids'][0].tolist()
    actual = inputs['input_ids'][0].tolist()
    length = 0
    for first, second in zip(candidate, actual[:-1]):
        if first != second or length >= 4096:
            break
        length += 1
    if 'linear_attention' in getattr(engine.model.config.get_text_config(),'layer_types',[]):
        length = length // 64 * 64
    return tuple(actual[:length]) if length >= 32 else ()


@torch.no_grad()
def cached(engine, inputs, ids, policy='default', bypass=None):
    stats = engine.diagnostics.setdefault('prefix',{'hits':0,'misses':0,'reused_tokens':0})
    stats['last_reused_tokens'] = 0
    stats['bypass_reason'], stats['math_policy'] = bypass, policy
    if not ids:
        return create(engine.model.config,engine.cfg['kv_quantization'])
    entries = engine.prefixes
    hit = next((entry for entry in entries if entry['ids']==ids and entry['math_policy']==policy),None)
    started = time.monotonic()
    if hit:
        entries.remove(hit)
        stats['hits'] += 1
        stats['last_reused_tokens'] = len(ids)
        stats['reused_tokens'] += len(ids)
    else:
        stats['misses'] += 1
        prefix = {key:value[..., :len(ids)] for key,value in inputs.items()
                  if key in ('input_ids','attention_mask','token_type_ids','mm_token_type_ids')}
        state = create(engine.model.config,'none')
        engine.model(**prefix,past_key_values=state,use_cache=True,logits_to_keep=1)
        hit = {'ids':ids,'math_policy':policy,'state':clone(state,'cpu')}
        del state
    entries.append(hit)
    del entries[:-2]
    stats['cpu_bytes'] = sum(t.numel()*t.element_size() for e in entries for t in tensors(e['state']))
    stats['prepare_seconds'] = time.monotonic()-started
    # Recompute multimodal positions for this request, never reuse another image's RoPE offsets.
    if hasattr(engine.model.model,'rope_deltas'):
        engine.model.model.rope_deltas = None
    return restore(hit['state'],engine.model.config,engine.cfg['kv_quantization'],engine.model.device)
