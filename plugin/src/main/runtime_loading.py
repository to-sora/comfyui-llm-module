import time
from . import ram_budget, weight_cache
from .load_transaction import admitted


def discard(owner):
    owner.engine = None
    owner.resident_bytes = 0


def account(owner):
    storage = owner.engine.diagnostics['storage']
    owner.resident_bytes = storage.get('cuda', 0)
    ram_budget.update(owner.key, sum(storage.values()), owner.resident_bytes)


def load(owner, device, budget, events):
    owner.ensure_engine()
    fresh = owner.engine.model is None
    if fresh:
        size = weight_cache.reservation(owner.cfg)
        staging = weight_cache.staging(owner.cfg, device, budget, size)
        with admitted(owner.key, size, staging, discard=lambda:discard(owner)):
            owner.engine.load(device, budget)
            account(owner)
    else:
        try:
            owner.engine.load(device, budget)
        except BaseException:
            # A failed restore must retain the already-owned weights and quota.
            from .residency import sizes
            owner.engine.diagnostics['storage'] = sizes(owner.engine.model)
            account(owner)
            raise
        account(owner)
    owner.loads += int(fresh)
    owner.transfers += int(not fresh)
    events.append({'time':time.time(), 'event':'loaded' if fresh else 'restored',
                  'model':owner.cfg['id'], 'resident_bytes':owner.resident_bytes,
                  'disk_loads':owner.loads})
