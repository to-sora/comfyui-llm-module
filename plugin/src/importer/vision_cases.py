import base64
from ..main.settings import APP

CASES = [("blue.png", "What color fills this image? Reply with one English word."),
         ("mug.png", "Name the main object in one English word."),
         ("car.png", "What color is the toy car? Reply with one English word."),
         ("car.png", "Is the background plain white or patterned? Reply with one word.")]


def messages(file, question):
    raw = (APP / "src/test/fixtures" / file).read_bytes()
    url = "data:image/png;base64," + base64.b64encode(raw).decode()
    return [{"role": "user", "content": [{"type": "image_url", "image_url": {"url": url}},
            {"type": "text", "text": question}]}]
