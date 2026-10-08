"""Explicit development diagnostic; executes within the ComfyUI model owner."""
import torch
from contextlib import ExitStack
from .kv_cache import create
from .prefix_cache import boundary
from .prefix_probe_modes import mode
from .prefix_probe_layers import Layers


@torch.no_grad()
def inspect(engine, request, inputs):
    model = engine.model
    length = len(boundary(engine, request, inputs))
    if not length or model.config.model_type != 'qwen3_5' or inputs['input_ids'].shape[-1] > 1024:
        raise ValueError('Diagnostic requires Qwen, a 64-token system prefix and at most 1024 input tokens')
    rows = []
    with ExitStack() as stack:
        stack.enter_context(mode(request['diagnostic_prefix']))
        stack.callback(setattr,model.model,'rope_deltas',None)
        hooks = Layers(model)
        stack.callback(hooks.close)
        model.model.rope_deltas = None
        positions = model._prepare_position_ids_for_generation(inputs['input_ids'], dict(inputs))
        full = model(**inputs, position_ids=positions, past_key_values=create(model.config,'none'),
                     use_cache=True, logits_to_keep=1, output_hidden_states=True)
        logits = full.logits.float().cpu()
        hidden = [t.detach().cpu() for t in full.hidden_states]
        del full
        prefix = {k:v[..., :length] for k,v in inputs.items()
                  if k in ('input_ids','attention_mask','token_type_ids','mm_token_type_ids')}
        state = create(model.config,'none')
        hooks.phase = 'prefix'
        first = model(**prefix, position_ids=positions[..., :length], past_key_values=state,
                      use_cache=True, logits_to_keep=1, output_hidden_states=True)
        for i,(before,after) in enumerate(zip(hidden,first.hidden_states)):
            delta = before[..., :length, :].float()-after.float().cpu()
            rows.append({'layer':i,'prefix_max':delta.abs().max().item(),
                         'prefix_mean':delta.abs().mean().item()})
        del first
        hooks.close()
        suffix = dict(inputs)
        for key in ('input_ids','token_type_ids','mm_token_type_ids'):
            if key in suffix:
                suffix[key] = suffix[key][..., length:]
        last = model(**suffix, position_ids=positions[..., length:], past_key_values=state,
                     use_cache=True, logits_to_keep=1, output_hidden_states=True)
        for row,before,after in zip(rows,hidden,last.hidden_states):
            delta = before[..., length:, :].float()-after.float().cpu()
            row['suffix_max'] = delta.abs().max().item()
        delta = logits-last.logits.float().cpu()
        engine.diagnostics['prefix_probe'] = {'mode':request['diagnostic_prefix'],'length':length,
            'layers':rows,'modules':hooks.rows,
            'logit_max':delta.abs().max().item(),'logit_mean':delta.abs().mean().item()}
