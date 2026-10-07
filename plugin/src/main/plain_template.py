import json


def parts(content):
    return [{"type": "text", "text": content or ""}] if not isinstance(content, list) else content


def adapt(messages, tools):
    """Use a model's instruction template when it has no native tool syntax."""
    if tools:
        instruction = ("Available tools: " + json.dumps(tools, ensure_ascii=False) +
            '\nWhen a tool is needed, output <tool_call>{"name":"tool_name","arguments":{...}}</tool_call>. '
            "Use only declared tools and arguments. Tool results will arrive in the next user turn. "
            "Use valid JSON with plain ASCII double quotes, never typographic quotes. "
            "Do not invent their results. Answer normally when no tool is needed.")
        if messages[0]["role"] == "system":
            previous = "\n".join(p["text"] for p in parts(messages[0]["content"]) if p["type"] == "text")
            messages[0]["content"] = previous + "\n" + instruction
        else:
            messages.insert(0, {"role": "system", "content": instruction})
    output = []
    for value in messages:
        msg = {"role": value["role"], "content": parts(value.get("content"))}
        for call in value.get("tool_calls", []):
            msg["content"].append({"type": "text", "text": "<tool_call>" +
                json.dumps(call["function"], ensure_ascii=False) + "</tool_call>"})
        if msg["role"] == "tool":
            msg["role"] = "user"
            msg["content"].insert(0, {"type": "text", "text": "Tool result " + value.get("tool_call_id", "") + ":\n"})
        if output and msg["role"] == output[-1]["role"]:
            output[-1]["content"] += [{"type": "text", "text": "\n\n"}] + msg["content"]
        else:
            output.append(msg)
    return output
