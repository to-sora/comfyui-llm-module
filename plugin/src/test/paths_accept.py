import json
from pathlib import Path
from .api_client import request
from .model_cases import user, image_message


def main():
    root = "/mnt/DATA9/LLM_model/d/"
    proof = []
    for folder, expected in [
        ("Qwen3.8-27B-OBLITERATED", "Qwen3.8-27B-OBLITERATED"),
        ("Qwen3.5-9B-gguf", "Qwen3.5-9B-gguf/Qwen3.5-9B-Uncensored-HauhauCS-Aggressive-Q6_K.gguf")]:
        answers = []
        for message, answer in [(user("What is 17 + 25? Reply with only the number."), "42"),
                                (image_message("blue"), "blue")]:
            result = request("/v1/chat/completions", {"model": root + folder,
                "messages": [message], "max_tokens": 32})
            text = result["choices"][0]["message"]["content"].strip().lower()
            assert answer in text, text
            answers.append(text)
        model = next(m for m in request("/llm/status")["models"] if m["loaded"])
        assert model["source"] == root + expected, model
        proof.append({"requested_directory": root + folder, "loaded_source": model["source"],
                      "backend": model["backend"], "answers": answers})
    Path("fan-out/directory-inputs.json").write_text(json.dumps({"status": "PASS", "cases": proof}, indent=2))
    print(json.dumps(proof))


if __name__ == "__main__":
    main()
