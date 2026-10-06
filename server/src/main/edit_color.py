import numpy as np
from PIL import Image, ImageColor, ImageEnhance, ImageFilter, ImageOps


def apply(image, operation, p):
    rgb, alpha = image.convert("RGB"), image.getchannel("A")
    enhance = {"brightness": ImageEnhance.Brightness, "contrast": ImageEnhance.Contrast,
               "saturation": ImageEnhance.Color, "sharpen": ImageEnhance.Sharpness}
    if operation in enhance:
        out = enhance[operation](rgb).enhance(p["factor"])
    elif operation == "gamma":
        table = [round(255 * (i / 255) ** (1 / p["gamma"])) for i in range(256)]
        out = rgb.point(table * 3)
    elif operation == "grayscale":
        out = ImageOps.grayscale(rgb).convert("RGB")
    elif operation == "invert":
        out = ImageOps.invert(rgb)
    elif operation == "autocontrast":
        out = ImageOps.autocontrast(rgb, cutoff=p["cutoff"])
    elif operation == "blur":
        out = rgb.filter(ImageFilter.GaussianBlur(p["radius"]))
    elif operation == "denoise":
        out = rgb.filter(ImageFilter.MedianFilter(int(p["size"])))
    elif operation == "threshold":
        out = rgb.convert("L").point(lambda x: 255 if x >= p["level"] else 0).convert("RGB")
    elif operation == "opacity":
        out = rgb
        alpha = alpha.point(lambda x: round(x * p["factor"]))
    elif operation == "remove_background":
        pixels = np.asarray(rgb, dtype=np.float32)
        border = np.concatenate((pixels[0], pixels[-1], pixels[:, 0], pixels[:, -1]))
        bg = ImageColor.getrgb(p["color"]) if p["color"] else np.median(border, axis=0)
        distance = np.sqrt(np.sum((pixels - bg) ** 2, axis=2))
        strength = np.clip((distance - p["tolerance"]) / max(p["softness"], 0.001), 0, 1)
        alpha = Image.fromarray((np.asarray(alpha) * strength).astype("uint8"))
        out = rgb
    else:
        raise ValueError("Unknown color operation")
    out.putalpha(alpha)
    return out
