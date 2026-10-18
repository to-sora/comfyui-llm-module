from transformers import TextStreamer
from .stream_text import VisibleText


class TokenStream(TextStreamer):
    def __init__(self, tokenizer, request):
        super().__init__(tokenizer, skip_prompt=True, skip_special_tokens=False)
        self.request = request
        self.visible = VisibleText()

    def on_finalized_text(self, text, stream_end=False):
        value = self.visible.feed(text, final=stream_end)
        if value:
            from .stream_bus import emit
            emit(self.request['comfy_prompt_id'],value)
