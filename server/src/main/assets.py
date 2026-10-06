import io
import uuid
from urllib.parse import urlencode
from PIL import Image, ImageOps
from .settings import DATA
from .records import create, get

Image.MAX_IMAGE_PIXELS = 4096 * 4096


def decode(data):
    with Image.open(io.BytesIO(data)) as raw:
        check_size(raw.size)
        return ImageOps.exif_transpose(raw).convert("RGBA")


def check_size(size):
    if any(type(n) is not int or n < 1 or n > 4096 for n in size):
        raise ValueError("Images must be at most 4096 × 4096 pixels")


def png(image):
    check_size(image.size)
    stream = io.BytesIO()
    image.save(stream, format="PNG")
    return stream.getvalue()


def save(db, sid, image, operation, parents=None, remote=None, **metadata):
    check_size(image.size)
    key = uuid.uuid4().hex
    thumb = image.copy()
    thumb.thumbnail((240, 180))
    thumb.save(DATA / "thumbs" / (key + ".png"))
    data = {"operation": operation, "parents": parents or [], "width": image.width,
            "height": image.height, "thumb": key + ".png", **metadata}
    if remote:
        data.update(remote=remote, bytes=len(png(image)))
    else:
        content = png(image)
        (DATA / "assets" / (key + ".png")).write_bytes(content)
        data.update(file=key + ".png", bytes=len(content))
    return create(db, sid, "image", data)


def resolve(db, sid, ident):
    value = get(db, sid, ident)
    if value["kind"] == "job":
        if value.get("status") != "done":
            raise ValueError(f"Image job #{ident} is not complete")
        value = get(db, sid, value["image"], "image")
    if value["kind"] != "image":
        raise ValueError("Expected an image or a completed image job")
    return value


async def load(db, comfy, sid, ident):
    value = resolve(db, sid, ident)
    if value.get("file"):
        raw = (DATA / "assets" / value["file"]).read_bytes()
    else:
        raw = await comfy.request("/view?" + urlencode(value["remote"]), binary=True)
    return decode(raw)
