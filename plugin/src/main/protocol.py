import time
import uuid


def response(model, result):
    return {"id": "chatcmpl-" + uuid.uuid4().hex, "object": "chat.completion",
            "created": int(time.time()), "model": model,
            "choices": [{"index": 0, "message": result["message"],
                         "finish_reason": result["finish_reason"]}],
            "usage": result["usage"]}


def validate(body):
    if not isinstance(body.get("model"), str):
        raise ValueError("model must be a string.")
    if not isinstance(body.get("messages"), list) or not body["messages"]:
        raise ValueError("messages must be a nonempty array.")
    if body.get("n", 1) != 1:
        raise ValueError("Only n=1 is supported; submit separate queued requests.")
    limit = body.get("max_completion_tokens", body.get("max_tokens", 256))
    if not isinstance(limit, int) or limit <= 0:
        raise ValueError("max_tokens must be a positive integer.")
    return body
