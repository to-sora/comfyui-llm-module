import numpy as np
from PIL import Image
from studio_helpers import ROOT


def verify(page,source_id):
    images=page['images']
    source=images[source_id]
    output=next(i for i in reversed(list(images.values()))
                if i['kind']=='generated' and i['parents']==[source_id])
    mask=images[output['recipe']['mask']]
    def pixels(item):
        return np.array(Image.open(ROOT/'server/data/assets'/item['file']).convert('RGBA'))
    original,edited=pixels(source),pixels(output)
    area=pixels(mask)[:,:,0]>0
    assert original.shape==edited.shape
    assert np.array_equal(original[~area],edited[~area])
    changed=int(np.any(original[area]!=edited[area],axis=1).sum())
    assert changed>0
    return {'outside_unchanged':True,'changed_pixels':changed,'output':output['id']}
