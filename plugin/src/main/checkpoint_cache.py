"""Public loader-node wrapper retaining checkpoint outputs for this process."""
from pathlib import Path
from .settings import APP, read
from . import ram_budget, weight_reads

CHECKPOINTS = {}


def native():
    from nodes import NODE_CLASS_MAPPINGS
    return NODE_CLASS_MAPPINGS['CheckpointLoaderSimple']


class LLMManagedCheckpoint:
    CATEGORY = 'LLM'
    RETURN_TYPES = ('MODEL','CLIP','VAE')
    FUNCTION = 'load'
    DESCRIPTION = 'ComfyUI checkpoint loader with process-lifetime RAM retention.'

    @classmethod
    def INPUT_TYPES(cls):
        return native().INPUT_TYPES()

    def load(self, ckpt_name):
        root = (APP / read('config.yaml')['comfy_directory']).resolve()
        path = root / 'models/checkpoints' / ckpt_name
        if not path.is_file():
            raise ValueError('RAM-managed checkpoints must be in ComfyUI models/checkpoints')
        identity=str(path.resolve())
        if identity in CHECKPOINTS:
            return CHECKPOINTS[identity]
        size = path.stat().st_size
        key = ('sdxl',str(path.resolve()))
        ram_budget.reserve(key,size,transient=size+2*ram_budget.GB,kind='sdxl')
        weight_reads.claim(str(path),'SDXL checkpoint')
        loader = native()()
        value = getattr(loader,loader.FUNCTION)(ckpt_name)
        CHECKPOINTS[identity] = value
        weight_reads.completed(str(path))
        patchers=[value[0],value[1].patcher,value[2].patcher]
        ram_budget.TRACKERS[key]=lambda:sum(p.loaded_size() for p in patchers
            if str(p.current_loaded_device()).startswith('cuda'))
        ram_budget.update(key,size)
        return value
