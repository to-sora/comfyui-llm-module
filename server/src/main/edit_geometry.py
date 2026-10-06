import math
from PIL import Image, ImageOps
from .assets import check_size


def apply(image, operation, p, overlay=None):
    if operation == "crop":
        x, y, w, h = (int(p[k]) for k in ("x", "y", "width", "height"))
        if x + w > image.width or y + h > image.height:
            raise ValueError("Crop lies outside the image")
        return image.crop((x, y, x + w, y + h))
    if operation == "resize":
        size = (int(p["width"]), int(p["height"]))
        check_size(size)
        return image.resize(size, Image.Resampling.LANCZOS)
    if operation == "rotate":
        if p["expand"]:
            a = math.radians(p["angle"])
            c, s = abs(math.cos(a)), abs(math.sin(a))
            check_size((round(c * image.width + s * image.height), round(s * image.width + c * image.height)))
        return image.rotate(p["angle"], resample=Image.Resampling.BICUBIC, expand=p["expand"])
    if operation == "flip":
        return ImageOps.mirror(image) if p["direction"] == "horizontal" else ImageOps.flip(image)
    if operation == "pad":
        l, t, r, b = (int(p[k]) for k in ("left", "top", "right", "bottom"))
        size = (image.width + l + r, image.height + t + b)
        check_size(size)
        out = Image.new("RGBA", size, p["color"])
        out.alpha_composite(image, (l, t))
        return out
    if operation == "overlay":
        out = image.copy()
        overlay = overlay.copy()
        overlay.putalpha(overlay.getchannel("A").point(lambda x: round(x * p["opacity"])))
        out.alpha_composite(overlay, (int(p["x"]), int(p["y"])))
        return out
    raise ValueError("Unknown geometry operation")
