from .errors import UserError
import io
import uuid
import hashlib
from urllib.parse import urlencode
from PIL import Image, ImageOps
from pillow_heif import register_heif_opener
from .settings import DATA
from .records import create, get

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


def save(db, sid, image, operation, parents=None, content=None, **metadata):
    check_size(image.size)
    key = uuid.uuid4().hex
    thumb = image.copy()
    thumb.thumbnail((240, 180))
    thumb.save(DATA / "thumbs" / (key + ".webp"), format="WEBP")
    data = {"operation": operation, "parents": parents or [], "width": image.width,
            "height": image.height, "thumb": key + ".webp", **metadata}
    content = png(image) if content is None else content
    (DATA / "assets" / (key + ".png")).write_bytes(content)
    data.update(file=key + ".png", bytes=len(content), sha256=hashlib.sha256(content).hexdigest())
    return create(db, sid, "image", data)


def resolve(db, sid, ident):
    value = get(db, sid, ident)
    if value["kind"] == "job":
        if value.get("status") != "done":
            raise UserError(f"Image job #{ident} is not complete")
        value = get(db, sid, value["image"], "image")
    if value["kind"] != "image":
        raise UserError("Expected an image or a completed image job")
    return value


async def load(db, comfy, sid, ident):
    value = resolve(db, sid, ident)
    if value.get("file"):
        raw = (DATA / "assets" / value["file"]).read_bytes()
    else:
        raw = await comfy.request("/view?" + urlencode(value["remote"]), binary=True)
    return decode(raw)
