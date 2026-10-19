from types import SimpleNamespace
import weakref
import torch
from ..main import ram_budget, weight_reads


class Engine:
    def __init__(self, source, key, seen, fail=False):
        self.model = None
        self.diagnostics = {}
        self.source, self.key, self.seen, self.fail = source, key, seen, fail

    def load(self, device, budget):
        if self.model is None:
            weight_reads.claim(self.source, 'fixture', (self.source, 'fixture'))
            self.model = torch.nn.Linear(128, 128, bias=False)
            self.seen.append(weakref.ref(self.model))
            ram_budget.TRACKERS[self.key] = lambda model=self.model:0
        if self.fail:
            raise OSError('Simulated interrupted model read/transfer')
        from ..main.residency import sizes
        self.diagnostics['storage'] = sizes(self.model)
        weight_reads.completed(self.source)


def owner(source, seen, fail=False):
    key = ('fixture', source)
    return SimpleNamespace(cfg={'id':source}, key=key, resident_bytes=0,
        loads=0, transfers=0, ensure_engine=lambda:None,
        engine=Engine(source,key,seen,fail))
