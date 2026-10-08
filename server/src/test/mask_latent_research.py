import asyncio
import gzip
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from .native_image_probe import generate
from .mask_crop_research import info

root = Path(__file__).resolve().parents[3]
out = root/'fan-out/studio-chat'


async def main():
    previous = info(json.loads((out/'vision-prefix-mask.json').read_text())['output'])
    p = previous['recipe']
    source,thin = [Image.open(root/'server/data/assets'/info(p[key])['file']).convert(kind)
                   for key,kind in (('source','RGBA'),('mask','L'))]
    large = Image.new('L',source.size)
    ImageDraw.Draw(large).ellipse((350,350,690,650),fill=255)
    rows = []
    for area,mask in (('thin',thin),('large',large)):
        for strength in (.5,.7,.99):
            for preserve in (False,True):
                params = {**p,'denoise':strength}
                output,trace = await generate(params,source,mask,preserve=preserve)
                result = Image.composite(output,source,mask)
                untouched = np.array(mask)==0
                assert np.array_equal(np.array(source)[untouched],np.array(result)[untouched])
                name = f'mask-latent-{area}-{strength}-{int(preserve)}'
                result.save(out/(name+'.png'))
                rows.append({'variant':name,'trace':trace,'file':name+'.png',
                             'outside_unchanged':True,'mask_box':mask.getbbox()})
                (out/'mask-latent-research.json.gz').write_bytes(
                    gzip.compress(json.dumps(rows,indent=2).encode()))
                print(name,round(trace['seconds'],2),'unmasked pixels exact',flush=True)


asyncio.run(main())
