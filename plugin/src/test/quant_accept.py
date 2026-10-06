import json
from pathlib import Path
from .api_client import request
from .model_cases import user, image_message


def main():
    proof = []
    for mode in ["bnb_fp4", "bnb_int8", "none"]:
        answers = []
        for message, expected in [(user("What is 6 times 9? Reply with only the number."), "54"),
                                  (image_message("blue"), "blue")]:
            result = request("/v1/chat/completions", {"model": "Qwen3.5-9B",
                "quantization": mode, "kv_quantization": "none", "messages": [message],
                "temperature": 0, "max_tokens": 32})
            answer = result["choices"][0]["message"]["content"].strip().lower()
            assert expected in answer, (mode, expected, answer)
            answers.append(answer)
        model = next(m for m in request("/llm/status")["models"] if m["loaded"])
        assert model["quantization"] == mode
        modules = model["diagnostics"]["weight_modules"]
        assert (modules == 0) == (mode == "none")
        assert model["diagnostics"]["kv"]["quantized_layers"] == 0
        proof.append({"quantization": mode, "answers": answers,
                      "weight_modules": modules, "resident_bytes": model["resident_bytes"]})
        print(json.dumps(proof[-1]), flush=True)
    path = Path(__file__).resolve().parents[3] / "fan-out/weight-modes.json"
    path.write_text(json.dumps({"status": "PASS", "cases": proof}, indent=2))


if __name__ == "__main__":
    main()
