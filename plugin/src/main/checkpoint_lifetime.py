"""Native cache owns idle checkpoints; active turns hold shared references."""
import weakref
from . import ram_budget, weight_reads

CHECKPOINTS = weakref.WeakValueDictionary()
TURNS = {}


def retired(key, token, source):
    ram_budget.release(key, token)
    receipt = weight_reads.READS.get(source)
    if receipt and receipt['state']=='resident':
        receipt['state']='released'


class Entry:
    def __init__(self, source, values, key, token):
        self.source, self.values = source, values
        self.patchers = (values[0], values[1].patcher, values[2].patcher)
        weakref.finalize(self, retired, key, token, source)

    def gpu(self):
        return sum(p.loaded_size() for p in self.patchers
                   if str(p.current_loaded_device()).startswith('cuda'))

    def _comfy_cache_tensors(self):
        return [t for p in self.patchers for t in
                (*p.model.parameters(), *p.model.buffers())]

    def outputs(self):
        return (*self.values, self)


def pin(token, source, entry=None):
    if not token:
        return
    with ram_budget.LOCK:
        turn = TURNS.get(token)
        if turn is None or source not in turn['sources']:
            raise ValueError('Checkpoint is not reserved by this active turn')
        if entry is not None:
            turn['entries'][source] = entry


def release(token):
    with ram_budget.LOCK:
        TURNS.pop(token, None)


def retain(entry):
    with ram_budget.LOCK:
        for turn in TURNS.values():
            if entry.source in turn['sources']:
                turn['entries'][entry.source] = entry


def snapshot():
    with ram_budget.LOCK:
        return {'turns':{k:list(v['sources']) for k,v in TURNS.items()},
                'resident':[{'source':k,'gpu_bytes':v.gpu(),
                    'turns':[t for t,value in TURNS.items() if k in value['entries']]}
                    for k,v in list(CHECKPOINTS.items())]}
