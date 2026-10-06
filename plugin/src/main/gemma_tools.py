import json
import re
import uuid


def arguments(text):
    position = 0
    def value():
        nonlocal position
        while position < len(text) and text[position].isspace():
            position += 1
        if text.startswith('<|"|>', position):
            start = position + 5
            position = text.index('<|"|>', start) + 5
            return text[start:position - 5]
        opening = text[position]
        if opening in "{[":
            position += 1
            result = {} if opening == "{" else []
            closing = "}" if opening == "{" else "]"
            while True:
                while text[position].isspace():
                    position += 1
                if text[position] == closing:
                    position += 1
                    return result
                item = value()
                if opening == "{":
                    while text[position].isspace():
                        position += 1
                    if text[position] != ":":
                        raise ValueError("Malformed Gemma tool argument.")
                    position += 1
                    result[item] = value()
                else:
                    result.append(item)
                while text[position].isspace():
                    position += 1
                if text[position] == ",":
                    position += 1
        token = re.match(r"[^\s{},\[\]:]+", text[position:])
        if token is None:
            raise ValueError("Malformed Gemma tool value.")
        raw = token.group()
        position += len(raw)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return raw
    return value()


def parse(text, tools):
    allowed = {t["function"]["name"] for t in tools or []}
    calls = []
    pattern = r"<\|tool_call>call:([^{}]+)(\{.*?\})<tool_call\|>"
    for name, raw in re.findall(pattern, text, re.S):
        if name not in allowed:
            raise ValueError(f"Model requested an undeclared tool: {name}")
        calls.append({"id": "call_" + uuid.uuid4().hex, "type": "function",
                      "function": {"name": name, "arguments": json.dumps(arguments(raw))}})
    text = re.sub(pattern, "", text, flags=re.S)
    text = re.sub(r"<\|channel>thought.*?<channel\|>", "", text, flags=re.S)
    for token in ("<bos>", "<eos>", "<|turn>", "<turn|>", "<|channel>", "<channel|>"):
        text = text.replace(token, "")
    text = text.strip()
    message = {"role": "assistant", "content": text or None}
    if calls:
        message["tool_calls"] = calls
    return message
