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
    p = info(json.loads((out/'vision-prefix-mask.json').read_text())['output'])['recipe']
    source,thin = [Image.open(root/'server/data/assets'/info(p[key])['file']).convert(kind)
                   for key,kind in (('source','RGBA'),('mask','L'))]
    large = Image.new('L',source.size)
    ImageDraw.Draw(large).ellipse((350,350,690,650),fill=255)
    prompts = [
        'A studio photograph of a blue ceramic cup with one vivid red five-pointed star painted on the bottom of its interior. The small red star is visible inside the cup. Glossy blue ceramic, same cup and background.',
        'A single bright red five-pointed star painted on a glossy blue ceramic surface, blue cup interior, photograph, vivid red star.']
    rows = []
    for area,mask in (('thin',thin),('large',large)):
        for strength in (.5,.7):
            for index,prompt in enumerate(prompts):
                output,trace = await generate({**p,'prompt':prompt,'denoise':strength},source,mask,preserve=True)
                result = Image.composite(output,source,mask)
                untouched = np.array(mask)==0
                assert np.array_equal(np.array(source)[untouched],np.array(result)[untouched])
                name = f'mask-prompt-{area}-{strength}-{index}'
                result.save(out/(name+'.png'))
                rows.append({'variant':name,'trace':trace,'file':name+'.png',
                             'outside_unchanged':True,'mask_box':mask.getbbox()})
                (out/'mask-prompt-research.json.gz').write_bytes(
                    gzip.compress(json.dumps(rows,indent=2).encode()))
                print(name,round(trace['seconds'],2),'unmasked pixels exact',flush=True)


asyncio.run(main())
