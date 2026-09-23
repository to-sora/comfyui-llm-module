import json
from client import DATA


def graph(mode="single", image=False, batch=False):
    model = json.loads((DATA / "acceptance-model.json").read_text())["model"]
    result = {
        "1": {"class_type": "QwenLoader", "inputs": {
            "model": model, "backend": "transformers", "quantization": "auto",
            "mode": mode, "gguf_file": "", "mmproj_file": ""}},
        "2": {"class_type": "QwenBatch" if batch else "QwenGenerate", "inputs": {
            "model": ["1", 0], "prompt": "State the sum of 2 and 3.",
            "prefix": "assistant", "max_tokens": 64, "temperature": 0.0}}}
    if image:
        result["3"] = {"class_type": "LoadImage", "inputs": {"image": "red.png"}}
        result["2"]["inputs"].update(images=["3", 0],
            prompt="Name the color filling the image.", prefix="caption")
    if batch:
        result["2"]["inputs"]["prompt"] = json.dumps(
            ["State the sum of 2 and 3.", "Name a primary color.",
             "State the sum of 3 and 4.", "Name a geometric shape."])
    return result
