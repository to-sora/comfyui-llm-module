from .errors import UserError
import functools
import subprocess
from PIL import ImageFont


@functools.lru_cache(maxsize=1)
def catalog():
    text = subprocess.check_output(["fc-list", "--format", "%{family[0]}|%{style[0]}|%{file}|%{index}\n"], text=True)
    result = {}
    for line in text.splitlines():
        family, style, path, index = line.split("|", 3)
        result.setdefault(family, []).append((style.lower(), path, int(index or 0)))
    return result


def load(p):
    choices = catalog().get(p["font"])
    if not choices:
        raise UserError("Unknown font family; select an installed font")
    def score(item):
        style = item[0]
        return (int(("bold" in style) == p["bold"]) +
                int(any(s in style for s in ("italic", "oblique")) == p["italic"]))
    style, path, index = max(choices, key=score)
    font = ImageFont.truetype(path, int(p["size"]), index=index)
    return font, p["bold"] and "bold" not in style, p["italic"] and not any(
        s in style for s in ("italic", "oblique"))
