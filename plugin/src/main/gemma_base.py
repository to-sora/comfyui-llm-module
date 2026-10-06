"""Completion protocol for the supplied pretrained Gemma checkpoint."""
from transformers import StopStringCriteria
from .tool_calls import parse

STOPS = ["\nQuestion:", "\nTools:", "\nTool result:", "\nInstructions:"]


def stopping(tokenizer):
    return StopStringCriteria(tokenizer=tokenizer, stop_strings=STOPS)


def response(text, request):
    for marker in STOPS:
        text = text.split(marker, 1)[0]
    choice = request.get("tool_choice")
    if request.get("tools") and (choice == "required" or isinstance(choice, dict)):
        text = "<tool_call>" + text
    return parse(text, request.get("tools"))
