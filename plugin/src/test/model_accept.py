import json
import sys
import time
from pathlib import Path
from .api_client import request
from .model_cases import TOOL, image_message, user


def main():
    name, kv = sys.argv[1:3]
    started = time.monotonic()
    base = {"model": name, "kv_quantization": kv, "max_tokens": 128, "temperature": 0}
    responses = {}
    def chat(messages, **kwargs):
        result = request("/v1/chat/completions", dict(base, messages=messages, **kwargs))
        print(json.dumps(result, ensure_ascii=False), flush=True)
        return result["choices"][0]["message"]
    question = user("What is 17 + 25? Reply with only the number.")
    responses["text"] = chat([question])["content"]
    assert responses["text"].strip() == "42"
    for color in ["red", "blue"]:
        answer = chat([image_message(color)])["content"]
        responses[color + "_image"] = answer
        assert color in answer.lower(), answer
    prompt = user("Use get_weather to check the weather in Hong Kong.")
    assistant = chat([prompt], tools=[TOOL])
    call = assistant["tool_calls"][0]
    assert call["function"]["name"] == "get_weather"
    args = json.loads(call["function"]["arguments"])
    assert args["city"].replace(" ", "").lower() == "hongkong", args
    responses["tool_call"] = call["function"]
    result = {"role": "tool", "tool_call_id": call["id"], "name": "get_weather",
              "content": '{"city":"Hong Kong","temperature_c":28,"condition":"sunny"}'}
    answer = chat([prompt, assistant, result, user("What is the temperature in Celsius? Reply with only the number.")], tools=[TOOL])
    assert "28" in answer["content"], answer
    responses["tool_result"] = answer["content"]
    responses["text_after_vision"] = chat([question])["content"]
    assert responses["text_after_vision"].strip() == "42"
    state = request("/llm/status")
    live = next(m for m in state["models"] if m["loaded"] and m["model"] == name)
    evidence = {"status": "PASS", "model": name, "kv_quantization": kv,
                "quantization": live["quantization"], "responses": responses,
                "resident_bytes": live["resident_bytes"], "seconds": time.monotonic() - started}
    path = Path(__file__).resolve().parents[3] / "fan-out" / f"model-{name}-{kv}.json"
    path.write_text(json.dumps(evidence, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
