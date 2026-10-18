import json
import torch


class BatchNoise:
    def __init__(self, seeds):
        self.seeds, self.seed = seeds, seeds[0]

    def generate_noise(self, latent):
        samples = latent['samples']
        if samples.shape[0] != len(self.seeds):
            raise ValueError('One random seed is required for each image in the batch')
        from nodes import NODE_CLASS_MAPPINGS
        cls=NODE_CLASS_MAPPINGS['RandomNoise']
        loader=cls()
        return torch.cat([getattr(loader,cls.FUNCTION)(seed)[0].generate_noise(
            {**latent,'samples':samples[i:i+1]}) for i,seed in enumerate(self.seeds)],dim=0)


class LLMBatchNoise:
    CATEGORY = 'LLM/image tools'
    RETURN_TYPES = ('NOISE',)
    FUNCTION = 'build'

    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {'seeds': ('STRING', {'default': '[0]'})}}

    def build(self, seeds):
        values = json.loads(seeds)
        if not isinstance(values, list) or not values or any(type(v) is not int or not 0 <= v < 2**64 for v in values):
            raise ValueError('Seeds must be an array of unsigned 64-bit integers')
        return (BatchNoise(values),)
