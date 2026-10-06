"""Stock, unquantized Gemma diagnostic; does not count as module acceptance."""
import json
import time
from pathlib import Path
import torch
from PIL import Image
from transformers import AutoModelForImageTextToText, AutoProcessor
from .api_client import request
from .model_cases import TOOL, user


def load_reference():
    app = Path(__file__).resolve().parents[2]
    model_path = "/mnt/DATA9/LLM_model/d/gemma-4-E2B"
    queue = request("/queue")
    if queue["queue_running"] or queue["queue_pending"]:
        raise RuntimeError("Run this diagnostic only with an idle ComfyUI queue.")
    request("/free", {"unload_models": True, "free_memory": True}, binary=True)
    for _ in range(30):
        if not request("/llm/status")["managed_models"]:
            break
        time.sleep(1)
    else:
        raise RuntimeError("ComfyUI has not released its models.")
    processor = AutoProcessor.from_pretrained(model_path, local_files_only=True)
    processor.chat_template = (app / ".local-tool-app/templates/gemma4.jinja").read_text()
    model = AutoModelForImageTextToText.from_pretrained(
        model_path, dtype=torch.bfloat16, device_map={"": "cuda:0"},
        attn_implementation="sdpa", local_files_only=True).eval()
    return app, model, processor


def main():
    app, model, processor = load_reference()
    evidence = {"type": "diagnostic, not acceptance", "source": model.config._name_or_path,
                "quantization": "none", "cache": "stock default", "responses": {}}
    def generate(name, inputs):
        inputs = inputs.to(model.device)
        count = inputs["input_ids"].shape[-1]
        with torch.inference_mode():
            output = model.generate(**inputs, max_new_tokens=64, do_sample=False)
        answer = processor.decode(output[0, count:], skip_special_tokens=False)
        evidence["responses"][name] = answer
        print(name, repr(answer), flush=True)
    def chat(messages, **kwargs):
        return processor.apply_chat_template(messages, tokenize=True, add_generation_prompt=True,
            return_dict=True, return_tensors="pt", enable_thinking=False, **kwargs)
    generate("completion", processor(text="17 + 25 =", return_tensors="pt"))
    generate("chat", chat([user("What is 17 + 25? Reply with only the number.")]))
    for color in ("red", "blue"):
        picture = Image.new("RGB", (256, 256), color)
        prompt = processor.image_token + "\nQuestion: What color is this image?\nAnswer:"
        generate(color, processor(text=prompt, images=picture, return_tensors="pt"))
    generate("tool", chat([user("Use get_weather to check the weather in Hong Kong.")], tools=[TOOL]))
    (app.parent / "fan-out/gemma-reference.json").write_text(json.dumps(evidence, indent=2))


if __name__ == "__main__":
    main()
