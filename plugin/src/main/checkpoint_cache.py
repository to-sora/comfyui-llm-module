"""Public loader wrapper with native caching and active-turn retention."""
import weakref
from .settings import APP, read
from . import ram_budget, weight_reads, ram_cleanup
from .load_transaction import admitted
from .checkpoint_lifetime import CHECKPOINTS, Entry, pin, retain


def native():
    from nodes import NODE_CLASS_MAPPINGS
    return NODE_CLASS_MAPPINGS['CheckpointLoaderSimple']


def path_for(name):
    root = (APP/read('config.yaml')['comfy_directory']).resolve()/'models/checkpoints'
    if name not in native().INPUT_TYPES()['required']['ckpt_name'][0]:
        raise ValueError('Choose an available SDXL checkpoint')
    path = root/name
    if not path.is_file():
        raise ValueError('Checkpoint file is unavailable')
    return path.resolve()


def load_checkpoint(name, path, key, size, token):
    weight_reads.checkpoint_claim(str(path))
    loader = native()()
    values = getattr(loader,loader.FUNCTION)(name)
    entry = Entry(str(path), values, key, token)
    ref = weakref.ref(entry)
    ram_budget.TRACKERS[key] = lambda: ref().gpu() if ref() is not None else 0
    ram_budget.update(key,size)
    weight_reads.completed(str(path))
    return entry


class LLMManagedCheckpoint:
    CATEGORY = 'LLM'
    RETURN_TYPES = ('MODEL','CLIP','VAE','LLM_CHECKPOINT')
    FUNCTION = 'load'
    DESCRIPTION = 'Native ComfyUI caching; active turns retain shared checkpoint weights.'

    @classmethod
    def INPUT_TYPES(cls):
        fields = native().INPUT_TYPES()
        return {**fields, 'optional':{**fields.get('optional',{}),
                                      'lease':('STRING',{'default':''})}}

    def load(self, ckpt_name, lease=''):
        path = path_for(ckpt_name)
        identity = str(path)
        pin(lease,identity)
        entry = CHECKPOINTS.get(identity)
        if entry is None:
            ram_cleanup.reclaim()
            size, key = path.stat().st_size, ('sdxl',identity)
            with admitted(key,size,size+2*ram_budget.GB,'sdxl'):
                token = ram_budget.RESERVATIONS[key]
                entry = load_checkpoint(ckpt_name,path,key,size,token)
                CHECKPOINTS[identity] = entry
        retain(entry)
        pin(lease,identity,entry)
        return entry.outputs()
