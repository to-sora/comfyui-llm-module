import numpy as np
import torch
from PIL import Image
from comfy import model_management as mm
from .background_patcher import PATCHER
from .background_model import mask
from .ram_budget import check,returning


class LLMRemoveBackground:
    CATEGORY='LLM/Image'
    RETURN_TYPES=('IMAGE',)
    FUNCTION='remove'

    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{'image':('IMAGE',)}}

    def remove(self,image):
        check(1024**3,returning())
        mm.load_models_gpu([PATCHER],memory_required=512*1024**2)
        results=[]
        for frame in image:
            mm.throw_exception_if_processing_interrupted()
            picture=Image.fromarray((frame.cpu().numpy().clip(0,1)*255).astype('uint8')).convert('RGBA')
            alpha=np.asarray(mask(picture),dtype=np.float32)/255
            rgba=np.asarray(picture,dtype=np.float32)/255
            rgba[:,:,3]*=alpha
            results.append(torch.from_numpy(rgba))
        return (torch.stack(results),)
