from .api_client import request


class Flow:
    def __init__(self, base):
        self.base, self.repairs = base, []

    def chat(self, messages, **extra):
        def complete(conversation):
            reply = request("/v1/chat/completions", {**self.base, "messages": conversation, **extra})
            return reply["choices"][0]["message"]
        message = complete(messages)
        if message.get("tool_parse_error"):
            self.repairs.append(message)
            message = complete([*messages, message, {"role": "user", "content":
                "Repair your tool call: " + message["tool_parse_error"]}])
            assert not message.get("tool_parse_error"), message
        return message

    def status(self):
        return next(m for m in request("/llm/status")["models"] if m["model"] == self.base["model"]
                    and m["quantization"] == self.base["quantization"])
