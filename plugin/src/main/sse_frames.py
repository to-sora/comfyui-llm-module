import json
import time
import uuid


class Frames:
    def __init__(self, response, model):
        self.response = response
        self.meta = {"id": "chatcmpl-" + uuid.uuid4().hex, "created": int(time.time()),
                     "model": model, "object": "chat.completion.chunk"}

    async def value(self, value):
        await self.response.write(("data: " + json.dumps(value, ensure_ascii=False) + "\n\n").encode())

    async def delta(self, delta, finish=None, **extra):
        await self.value({**self.meta, "choices": [{"index": 0, "delta": delta,
                          "finish_reason": finish}], **extra})

    async def done(self):
        await self.response.write(b"data: [DONE]\n\n")
        await self.response.write_eof()
