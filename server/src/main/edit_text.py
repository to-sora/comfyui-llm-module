from PIL import Image, ImageDraw
from .fonts import load


def apply(image, p):
    font, bold, italic = load(p)
    layer = Image.new("RGBA", image.size)
    draw = ImageDraw.Draw(layer)
    width = int(p["width"])
    y = int(p["y"])
    stroke = int(p["stroke_width"])
    lines = []
    for paragraph in p["text"].split("\n"):
        line = ""
        for char in paragraph:
            if line and draw.textlength(line + char, font=font) > width - p["indent"]:
                lines.append(line)
                line = ""
            line += char
        lines.append(line)
    for line in lines:
        length = draw.textlength(line, font=font)
        offset = {"left": p["indent"], "center": (width - length) / 2, "right": width - length}[p["align"]]
        draw.text((p["x"] + offset, y), line, fill=p["color"], font=font,
                  stroke_width=stroke + int(bold), stroke_fill=p["stroke_color"] if stroke else p["color"], anchor="lt")
        y += int(p["size"] + p["spacing"])
    if italic:
        layer = layer.transform(image.size, Image.Transform.AFFINE,
            (1, -0.18, 0.18 * p["y"], 0, 1, 0), Image.Resampling.BICUBIC)
    return Image.alpha_composite(image, layer)
