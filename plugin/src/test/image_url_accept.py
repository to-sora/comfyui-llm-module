import json
from pathlib import Path
import shutil
import sys
from .api_client import request, API


def main():
    shutil.copyfile("fan-out/sdxl-baseline.png", "plugin/data/input/uat-sdxl.png")
    message = {"role": "user", "content": [
        {"type": "text", "text": "Name the two main colors of the objects. Reply with just the color names."},
        {"type": "image_url", "image_url": {"url": API + "/view?filename=uat-sdxl.png&type=input"}}]}
    proof = []
    selected = [tuple(sys.argv[1:3])] if len(sys.argv) > 2 else [
        ("Qwen3.5-9B", "hqq_4"), ("Qwen3.5-9B-gguf", "q4_0")]
    for model, kv in selected:
        result = request("/v1/chat/completions", {"model": model, "kv_quantization": kv,
                         "messages": [message], "max_tokens": 32})
        answer = result["choices"][0]["message"]["content"].lower()
        assert "red" in answer and "blue" in answer, answer
        proof.append({"model": model, "answer": answer})
    suffix = "-" + sys.argv[1] if len(sys.argv) > 2 else ""
    Path(f"fan-out/image-url{suffix}.json").write_text(json.dumps({"status": "PASS",
        "input": "Actual SDXL output, fetched from ComfyUI's self-signed HTTPS image endpoint",
        "cases": proof}, indent=2))
    print(json.dumps(proof))


if __name__ == "__main__":
    main()
