class VisibleText:
    markers = ("<think>", "<tool_call>", "<|tool_call>", "<|im_end|>",
               "<|endoftext|>", "<|fim_suffix|>", "<eos>", "<end_of_turn>")

    def __init__(self):
        self.buffer = self.spaces = ""
        self.hidden = self.stopped = self.started = False

    def feed(self, text, final=False):
        self.buffer += text
        result = ""
        while self.buffer and not self.stopped:
            if self.hidden:
                end = self.buffer.find("</think>")
                if end < 0:
                    self.buffer = self.buffer[-7:]
                    break
                self.buffer = self.buffer[end+8:]
                self.hidden = False
                continue
            marker = next((m for m in self.markers if self.buffer.startswith(m)), None)
            if marker:
                self.buffer = self.buffer[len(marker):]
                if marker == "<think>":
                    self.hidden = True
                else:
                    self.stopped = True
                continue
            if not final and any(m.startswith(self.buffer) for m in self.markers):
                break
            result += self.buffer[0]
            self.buffer = self.buffer[1:]
        result = self.spaces + result
        if not self.started:
            result = result.lstrip()
        clean = result.rstrip()
        self.spaces = result[len(clean):]
        self.started |= bool(clean)
        return clean
