from .errors import UserError
import io
from PIL import Image, ImageOps
from pillow_heif import register_heif_opener
from .settings import DATA

Image.MAX_IMAGE_PIXELS = 100_000_000
register_heif_opener()


def decode(data, upload=False):
    with Image.open(io.BytesIO(data)) as raw:
        image = ImageOps.exif_transpose(raw)
        if upload:
            image.thumbnail((4096, 4096), Image.Resampling.LANCZOS)
        check_size(image.size)
        return image.convert("RGBA")


def check_size(size):
    if any(type(n) is not int or n < 1 or n > 4096 for n in size):
        raise UserError("Images must be at most 4096 × 4096 pixels")


def png(image):
    check_size(image.size)
    stream = io.BytesIO()
    image.save(stream, format="PNG")
    return stream.getvalue()
