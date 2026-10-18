import json
from ..graph import node


def build(p, seeds, source=None, mask=None):
    if p.get('operation')=='remove_background':
        return {'12':node('LoadImage',image=source),
                '10':node('LLMRemoveBackground',image=['12',0]),
                '11':node('SaveImage',images=['10',0],filename_prefix='studio/'+p['output_key'])}
    g = {'1':node('LLMManagedCheckpoint',ckpt_name=p['checkpoint']),
         '2':node('CLIPTextEncode',clip=['1',1],text=p['prompt']),
         '3':node('CLIPTextEncode',clip=['1',1],text=p.get('negative','')),
         '4':node('EmptyLatentImage',width=p['width'],height=p['height'],batch_size=len(seeds)),
         '5':node('KSamplerSelect',sampler_name=p['sampler_name']),
         '6':node('BasicScheduler',model=['1',0],scheduler=p['scheduler'],steps=p['steps'],denoise=p['denoise']),
         '7':node('CFGGuider',model=['1',0],positive=['2',0],negative=['3',0],cfg=p['cfg']),
         '8':node('LLMBatchNoise',seeds=json.dumps(seeds)),
         '9':node('SamplerCustomAdvanced',noise=['8',0],guider=['7',0],sampler=['5',0],sigmas=['6',0],latent_image=['4',0]),
         '10':node('VAEDecode',samples=['9',0],vae=['1',2]),
         '11':node('SaveImage',images=['10',0],filename_prefix='studio/'+p['output_key'])}
    if source:
        g['12'] = node('LoadImage',image=source)
        g['4'] = node('VAEEncode',pixels=['12',0],vae=['1',2])
    if mask:
        g['13'] = node('LoadImageMask',image=mask,channel='red')
        g['14'] = g['4']
        g['4'] = node('SetLatentNoiseMask',samples=['14',0],mask=['13',0])
    return g
