"""Only a different LLM selection can dispose of resident LLM weights."""
import time
from comfy import model_management as mm
from . import ram_budget, ram_cleanup, weight_cache, weight_reads
from .weight_identity import representation


def activate(owner, handles, events):
    if owner.engine is None or owner.engine.model is None:
        # Refuse an already retired/failed source before disturbing the current model.
        weight_reads.ensure_new(weight_cache.source(owner.cfg), representation(owner.cfg))
    previous = [h for h in handles.values() if h is not owner
                and h.engine is not None and h.engine.model is not None]
    if not previous:
        return
    mm.unload_all_models()
    for old in previous:
        source = old.engine.diagnostics.get('weight_source')
        old.engine = None
        old.resident_bytes = 0
        ram_budget.release(old.key, ram_budget.RESERVATIONS.get(old.key))
        if source:
            weight_reads.READS[weight_reads.identity(source)]['state'] = 'retired'
        events.append({'time':time.time(), 'event':'replaced', 'model':old.cfg['id'],
                       'replacement':owner.cfg['id'], 'disk_loads':old.loads})
    ram_cleanup.reclaim()
    mm.soft_empty_cache()
