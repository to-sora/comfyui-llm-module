import copy
import json


def normalize(request):
    messages = copy.deepcopy(request["messages"])
    for message in messages:
        if message.get("content") is None:
            message["content"] = ""
        for call in message.get("tool_calls", []):
            args = call["function"]["arguments"]
            if isinstance(args, str):
                call["function"]["arguments"] = json.loads(args)
    tools = request.get("tools")
    choice = request.get("tool_choice", "auto")
    if choice == "none":
        tools = None
    elif isinstance(choice, dict):
        name = choice["function"]["name"]
        tools = [t for t in tools or [] if t["function"]["name"] == name]
        if not tools:
            raise ValueError("Requested function is not in tools.")
    if choice == "required" or isinstance(choice, dict):
        instruction = "You must call one of the provided tools."
        if messages[0]["role"] == "system":
            content = messages[0]["content"]
            messages[0]["content"] = (content + "\n" + instruction if isinstance(content, str)
                else [*content, {"type": "text", "text": instruction}])
        else:
            messages.insert(0, {"role": "system", "content": instruction})
    return messages, tools
