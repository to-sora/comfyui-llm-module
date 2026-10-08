import asyncio
import gzip
import json
import ssl
import sys
import urllib.request
from pathlib import Path
import numpy as np
from PIL import Image
from .native_image_probe import generate
from ..main.generation import source_size

root = Path(__file__).resolve().parents[3]
out = root/'fan-out/studio-chat'


def info(ident):
    with urllib.request.urlopen('https://127.0.0.1:8189/api/images/'+ident+'/info',
                                 context=ssl._create_unverified_context()) as response:
        return json.load(response)


async def main():
    previous = info(json.loads((out/'vision-prefix-mask.json').read_text())['output'])
    p = previous['recipe']
    source,mask = [Image.open(root/'server/data/assets'/info(p[key])['file']).convert(kind)
                   for key,kind in (('source','RGBA'),('mask','L'))]
    left,top,right,bottom = mask.getbbox()
    box = (max(0,left-64),max(0,top-64),min(source.width,right+64),min(source.height,bottom+64))
    cropped,area = source.crop(box),mask.crop(box)
    dimensions = source_size(cropped.size)
    image = cropped.resize(dimensions,Image.Resampling.LANCZOS)
    region = area.resize(dimensions,Image.Resampling.NEAREST)
    rows = []
    preserve = len(sys.argv)>1 and sys.argv[1]=='source'
    label = 'mask-crop-source' if preserve else 'mask-crop'
    variants = ((.5,0),(.7,0)) if preserve else ((.5,0),(.5,6),(.7,6))
    for strength,grow in variants:
        params = {**p,'width':dimensions[0],'height':dimensions[1],'denoise':strength}
        output,trace = await generate(params,image,region,grow,preserve)
        restored = source.copy()
        restored.paste(output.resize(cropped.size,Image.Resampling.LANCZOS),box[:2])
        result = Image.composite(restored,source,mask)
        original,final = np.array(source),np.array(result)
        untouched = np.array(mask)==0
        assert np.array_equal(original[untouched],final[untouched])
        name = f'{label}-{strength}-{grow}'
        result.save(out/(name+'.png'))
        rows.append({'variant':name,'box':box,'working_size':dimensions,'trace':trace,
                     'outside_unchanged':True,'file':name+'.png'})
        (out/(label+'-research.json.gz')).write_bytes(gzip.compress(json.dumps(rows,indent=2).encode()))
        print(name,round(trace['seconds'],2),'unmasked pixels exact',flush=True)


if __name__ == '__main__':
    asyncio.run(main())
