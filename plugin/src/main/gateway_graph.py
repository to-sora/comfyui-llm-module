import json
from .settings import read


def graph(body):
    options = {key: body[key] for key in
               ("quantization", "kv_quantization", "context_tokens", "backend", "mmproj")
               if key in body}
    inputs = dict(model=body["model"], quantization="default",
                  kv_quantization="none", context_tokens=read("config.yaml")["context_tokens"])
    inputs.update(options)
    return {
        "1": {"class_type": "LLMModel", "inputs": inputs},
        "2": {"class_type": "LLMChat", "inputs": {
            "model": ["1", 0], "messages": json.dumps(body["messages"]),
            "max_tokens": body.get("max_completion_tokens", body.get("max_tokens", 256)),
            "temperature": body.get("temperature", 0),
            "tools": json.dumps(body.get("tools", [])),
            "request_json": json.dumps(body)}},
    }
