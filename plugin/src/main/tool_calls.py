import json
import re
import uuid


def parse(text, tools):
    schemas = {t["function"]["name"]: t["function"] for t in tools or []}
    calls = []
    blocks = re.findall(r"<tool_call>(.*?)</tool_call>", text, re.S)
    for block in blocks:
        if block.strip().startswith("{"):
            obj = json.loads(block)
            name, args = obj["name"], obj["arguments"]
        else:
            function = re.search(r"<function=([^>]+)>(.*?)</function>", block, re.S)
            if function is None:
                raise ValueError("Malformed model tool call.")
            name, body = function.groups()
            properties = schemas.get(name, {}).get("parameters", {}).get("properties", {})
            args = {}
            for key, raw in re.findall(r"<parameter=([^>]+)>(.*?)</parameter>", body, re.S):
                value = raw.strip()
                if properties.get(key, {}).get("type") != "string":
                    try:
                        value = json.loads(value)
                    except json.JSONDecodeError:
                        if properties.get(key, {}).get("type") in {"number", "integer", "boolean", "object", "array"}:
                            raise ValueError(f"Invalid tool argument: {key}")
                args[key] = value
        if name not in schemas:
            raise ValueError(f"Model requested an undeclared tool: {name}")
        if isinstance(args, str):
            args = json.loads(args)
        if not isinstance(args, dict):
            raise ValueError("Tool arguments must be an object.")
        missing = set(schemas[name].get("parameters", {}).get("required", [])) - args.keys()
        if missing:
            raise ValueError(f"Missing required tool arguments: {sorted(missing)}")
        calls.append({"id": "call_" + uuid.uuid4().hex, "type": "function",
                      "function": {"name": name, "arguments": json.dumps(args, ensure_ascii=False)}})
    content = re.sub(r"<tool_call>.*?</tool_call>", "", text, flags=re.S)
    if "<tool_call>" in content:
        raise ValueError("Incomplete tool call; increase max_tokens.")
    content = re.sub(r"<think>.*?</think>", "", content, flags=re.S)
    for token in ("<|im_end|>", "<|endoftext|>", "<|fim_suffix|>", "<eos>", "<end_of_turn>"):
        content = content.replace(token, "")
    message = {"role": "assistant", "content": content.strip() or None}
    if calls:
        message["tool_calls"] = calls
    return message
