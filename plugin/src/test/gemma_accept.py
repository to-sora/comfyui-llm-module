"""Additional real-model checks for the instruction model."""
import json
import sys
from pathlib import Path
from .api_client import request
from .model_cases import TOOL, image_message, user


def main():
    kv = sys.argv[1] if len(sys.argv) > 1 else "hqq_8"
    root = Path(__file__).resolve().parents[3]
    evidence = {"model": "gemma-3-12b-it", "kv_quantization": kv}
    def chat(messages, **extra):
        body = dict(model=evidence["model"], kv_quantization=kv, messages=messages,
                    max_tokens=128, temperature=0, parallel_tool_calls=False)
        answer = request("/v1/chat/completions", dict(body, **extra))
        print(json.dumps(answer), flush=True)
        return answer["choices"][0]["message"], answer["usage"]
    message, _ = chat([user("What is 9 times 6? Reply with only the number.")])
    assert message["content"].strip() == "54", message
    evidence["math"] = message["content"]
    message, _ = chat([image_message("green")])
    assert "green" in message["content"].lower(), message
    evidence["green_image"] = message["content"]
    calc = {"type": "function", "function": {"name": "multiply",
        "description": "Multiply two integers.", "parameters": {"type": "object",
        "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}}, "required": ["a", "b"]}}}
    for choice in ("required", {"type": "function", "function": {"name": "multiply"}}):
        message, _ = chat([user("Use multiply to multiply 4 and 13.")],
                           tools=[TOOL, calc], tool_choice=choice)
        calls = message["tool_calls"]
        assert len(calls) == 1 and calls[0]["function"]["name"] == "multiply", message
        assert json.loads(calls[0]["function"]["arguments"]) == {"a": 4, "b": 13}, message
        evidence[str(choice)] = calls[0]["function"]
    prompt = (root / "README.md").read_text() + "\nWhich port serves the LLM gateway? Reply with only the number."
    message, usage = chat([user(prompt)])
    assert usage["prompt_tokens"] > 512, usage
    assert message["content"].strip().rstrip(".") == "8188", message
    evidence["document"] = dict(answer=message["content"], **usage)
    evidence["status"] = "PASS"
    (root / "fan-out" / f"gemma-extra-{kv}.json").write_text(json.dumps(evidence, indent=2))


if __name__ == "__main__":
    main()
