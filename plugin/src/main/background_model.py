"""U2NetP saliency on CPU, retained for the ComfyUI process lifetime."""
import hashlib
import numpy as np
from PIL import Image
from .settings import APP
from . import ram_budget,weight_reads

PATH=APP/'data/image-models/u2netp.onnx'
SESSION=None


def load():
    global SESSION
    if SESSION is not None:
        return
    import onnxruntime as ort
    if not PATH.is_file():
        raise FileNotFoundError('Install the background model with plugin/install-image-tools.sh')
    ram_budget.reserve(('aux','u2netp'),256*1024**2,512*1024**2,kind='aux')
    weight_reads.claim(str(PATH),'U2NetP CPU segmentation')
    raw=PATH.read_bytes()
    if hashlib.md5(raw).hexdigest()!='8e83ca70e441ab06c318d82300c84806':
        raise ValueError('The background model checksum does not match')
    options=ort.SessionOptions()
    options.intra_op_num_threads=4
    options.inter_op_num_threads=1
    SESSION=ort.InferenceSession(raw,sess_options=options,providers=['CPUExecutionProvider'])
    ram_budget.update(('aux','u2netp'),256*1024**2)
    weight_reads.completed(str(PATH))


def mask(image):
    sample=np.asarray(image.convert('RGB').resize((320,320),Image.Resampling.LANCZOS),dtype=np.float32)
    sample/=max(float(sample.max()),1e-6)
    sample=(sample-np.array([.485,.456,.406],dtype=np.float32))/np.array([.229,.224,.225],dtype=np.float32)
    values=SESSION.run(None,{SESSION.get_inputs()[0].name:sample.transpose(2,0,1)[None]})[0][0,0]
    low,high=float(values.min()),float(values.max())
    values=(values-low)/max(high-low,1e-6)
    return Image.fromarray((np.clip(values,0,1)*255).astype('uint8')).resize(image.size,Image.Resampling.LANCZOS)
