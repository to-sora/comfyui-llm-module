from .errors import UserError
from PIL import Image, ImageOps
from . import assets
from .generation import source_size


async def prepare(e, sid, p, key):
    source = mask = original = mask_image = None
    parents = []
    if "source" in p:
        original = await assets.load(e.db, e.comfy, sid, p["source"])
        parents.append(assets.resolve(e.db, sid, p["source"])["id"])
        if "mask" in p:
            mask_image = (await assets.load(e.db, e.comfy, sid, p["mask"])).convert("L")
            if mask_image.size != original.size:
                raise UserError("Mask dimensions must match the source")
            p["width"], p["height"] = ((n + 7) // 8 * 8 for n in original.size)
            padded = Image.new("RGBA", (p["width"], p["height"]))
            padded.paste(original, (0, 0))
            padded_mask = Image.new("L", padded.size)
            padded_mask.paste(mask_image, (0, 0))
            mask = await e.comfy.upload(assets.png(padded_mask), key + "-mask.png")
        else:
            p["width"], p["height"] = source_size(original.size)
            padded = ImageOps.pad(original, (p["width"], p["height"]), Image.Resampling.LANCZOS)
        source = await e.comfy.upload(assets.png(padded), key + ".png")
    return source, mask, original, mask_image, parents
