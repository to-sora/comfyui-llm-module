import json
from pathlib import Path
from urllib.error import HTTPError
from .api_client import request
from .model_cases import TOOL, user


def main():
    profiles = request("/v1/models")["data"]
    assert len(profiles) >= 5
    base = {"model": "Qwen3.5-9B", "kv_quantization": "hqq_4", "max_tokens": 96,
            "messages": [user("What is 17 + 25? Reply with only the number.")]}
    errors = []
    for body in [[], dict(base, messages=[]), dict(base, n=2),
                 dict(base, temperature=-1), dict(base, tools=[{"type": "function", "function": "bad"}])]:
        try:
            request("/v1/chat/completions", body)
            raise AssertionError("Invalid request was accepted")
        except HTTPError as error:
            assert error.code == 400, error.read()
            errors.append(json.loads(error.read())["error"]["message"])
    streams = {}
    for name, extra in [("text", {}), ("tool", {"tools": [TOOL], "parallel_tool_calls": False,
                         "messages": [user("Use get_weather for Hong Kong.")]})]:
        raw = request("/v1/chat/completions", dict(base, stream=True, **extra), binary=True).decode()
        assert raw.rstrip().endswith("data: [DONE]")
        chunks = [json.loads(line[6:]) for line in raw.splitlines()
                  if line.startswith("data: ") and line != "data: [DONE]"]
        delta = chunks[0]["choices"][0]["delta"]
        if name == "text":
            assert delta["content"].strip() == "42"
        else:
            call = delta["tool_calls"][0]
            assert call["index"] == 0
            assert json.loads(call["function"]["arguments"])["city"] == "Hong Kong"
        streams[name] = {"delta": delta, "finish_reason": chunks[-1]["choices"][0]["finish_reason"]}
    proof = {"status": "PASS", "invalid_requests": errors, "streams": streams}
    Path("fan-out/api.json").write_text(json.dumps(proof, indent=2))
    print(json.dumps(proof))


if __name__ == "__main__":
    main()
