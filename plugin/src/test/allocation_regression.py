"""Loader failures use tiny CPU tensors; no real model weights are read."""
from unittest.mock import patch
from ..main import ram_budget, weight_reads, runtime_loading, weight_cache
from .allocation_fixtures import owner, Engine


def run():
    seen, events = [], []
    failed = owner('allocation-failure',seen,True)
    baseline = dict(ram_budget.RESERVATIONS)
    with patch.object(weight_cache,'reservation',return_value=1024), \
            patch.object(weight_cache,'staging',return_value=0):
        try:
            runtime_loading.load(failed,'cpu',1024,events)
        except OSError:
            pass
        else:
            raise AssertionError('Expected a read failure')
        assert failed.engine is None and seen[0]() is None
        assert ram_budget.RESERVATIONS == baseline
        assert failed.key not in ram_budget.TRACKERS
        receipt = dict(weight_reads.READS['allocation-failure'])
        assert receipt['reads'] == 1 and receipt['state'] == 'failed'
        failed.engine = Engine('allocation-failure',failed.key,seen,True)
        try:
            runtime_loading.load(failed,'cpu',1024,events)
        except RuntimeError as exc:
            assert 'R2:' in str(exc)
        else:
            raise AssertionError('Failed weights must not be reread')
        assert ram_budget.RESERVATIONS == baseline
        assert weight_reads.READS['allocation-failure'] == receipt
        assert len(seen) == 1
        valid = owner('allocation-next-model',seen)
        runtime_loading.load(valid,'cpu',1024,events)
        model = valid.engine.model
        token = ram_budget.RESERVATIONS[valid.key]
        valid.engine.fail = True
        try:
            runtime_loading.load(valid,'cpu',1024,events)
        except OSError:
            pass
        else:
            raise AssertionError('Expected a restore failure')
        assert valid.engine.model is model
        assert ram_budget.RESERVATIONS[valid.key] is token
        assert weight_reads.READS['allocation-next-model']['state'] == 'resident'
        assert valid.loads == 1 and valid.transfers == 0
    return {'failed_quota_released':True,'failed_tensor_released':True,
        'failed_read_retained':True,'reread_refused_without_quota_leak':True,
        'next_model_loaded':True,'failed_restore_preserves_existing_weights_and_quota':True}


if __name__ == '__main__':
    print(run())
