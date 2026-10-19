import tempfile
from pathlib import Path
from unittest.mock import patch
from comfy import model_management as mm
from ..main import runtime, weight_reads
from ..main.settings import APP
from ..main.weight_identity import representation


def run():
    with tempfile.TemporaryDirectory(dir=APP/'data/tmp') as original, \
            tempfile.TemporaryDirectory(dir=APP/'data/quantized') as cached, \
            patch.object(runtime,'LLMPatcher',side_effect=lambda owner:object()):
        cfg={'id':'identity-fixture','model':original,'quantization':'bnb_nf4',
             'precision':'bfloat16','device':'auto'}
        auto=runtime.get_handle(cfg)
        explicit=runtime.get_handle({**cfg,'device':str(mm.get_torch_device())})
        assert auto.owner is explicit.owner
        assert auto.cfg['device'] == str(mm.get_torch_device())
        weight_reads.claim(original,'bnb_nf4',representation(cfg))
        weight_reads.completed(original)
        (Path(cached)/'source.txt').write_text(original)
        cache_cfg={**cfg,'model':cached}
        selected=runtime.get_handle(cache_cfg)
        assert selected.owner is auto.owner
        nested=Path(cached)/'nested'
        nested.mkdir()
        (nested/'source.txt').write_text(cached)
        assert runtime.get_handle({**cfg,'model':str(nested)}).owner is auto.owner
        try:
            weight_reads.claim(cached,'bnb_nf4',representation(cache_cfg))
        except RuntimeError as exc:
            assert 'R2:' in str(exc)
        else:
            raise AssertionError('New NF4 cache must not permit a duplicate read')
        assert weight_reads.identity(cached) not in weight_reads.READS
        assert weight_reads.READS[original]['reads'] == 1
    return {'auto_explicit_same_owner':True,'new_cache_same_owner':True,
            'source_to_new_cache_duplicate_refused':True,'weight_io':0}


if __name__ == '__main__':
    print(run())
