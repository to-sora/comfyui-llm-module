"""Compare actual decoding without changing the production prefix cache."""
import time
from .generation_controls import StopGeneration, single_tool
from .kv_cache import create
from .prefix_state import clone, restore
from .tool_calls import parse
from .model_response import parse as parse_response
from .prefix_probe_prefill import prefill


def compare(engine, request, inputs, length):
    model, processor = engine.model, engine.processor
    tokenizer = getattr(processor, 'tokenizer', processor)
    count = inputs['input_ids'].shape[-1]
    limit = min(64, request.get('max_completion_tokens', request.get('max_tokens', 64)))
    options = {'do_sample':False, 'max_new_tokens':limit, 'use_cache':True,
               'stopping_criteria':[StopGeneration(tokenizer,
                    '</tool_call>' if single_tool(request) else None)]}
    mode = engine.cfg['kv_quantization']
    rows = []

    def run(label, factory):
        model.model.rope_deltas = None
        started = time.monotonic()
        cache = factory()
        output = model.generate(**inputs, past_key_values=cache, **options)
        tokens = output[0, count:]
        raw = processor.decode(tokens, skip_special_tokens=False)
        message = parse_response(parse, raw, request.get('tools'))
        rows.append({'path':label, 'seconds':time.monotonic()-started,
                     'tokens':tokens.tolist(), 'raw':raw,
                     'content':message.get('content'),
                     'tools':[c['function'] for c in message.get('tool_calls',[])],
                     'parse_error':message.get('tool_parse_error')})

    run('full', lambda:create(model.config, mode))
    model.model.rope_deltas = None
    positions = model._prepare_position_ids_for_generation(inputs['input_ids'], dict(inputs))
    prefix = {key:value[..., :length] for key,value in inputs.items()
              if key in ('input_ids','attention_mask','token_type_ids','mm_token_type_ids')}
    state = create(model.config, 'none')
    started = time.monotonic()
    prefill(engine, request, prefix, position_ids=positions[..., :length], past_key_values=state,
          use_cache=True, logits_to_keep=1)
    saved = clone(state, 'cpu')
    prefill_seconds = time.monotonic()-started
    del state
    for label in ('restored', 'reused'):
        run(label, lambda:restore(saved, model.config, mode, model.device))
    return {'kv_quantization':mode, 'prefix_tokens':length, 'prefix_seconds':prefill_seconds,
            'token_limit':limit, 'runs':rows, 'timing_includes_cache_setup':True,
            'tokens_equal':all(r['tokens']==rows[0]['tokens'] for r in rows),
            'messages_equal':all((r['content'],r['tools'],r['parse_error'])==
                (rows[0]['content'],rows[0]['tools'],rows[0]['parse_error']) for r in rows)}
