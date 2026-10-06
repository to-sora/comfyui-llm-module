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
        messages.insert(0, {"role": "system", "content": "You must call one of the provided tools."})
    return messages, tools
