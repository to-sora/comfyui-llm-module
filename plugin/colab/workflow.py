def workflow(prompt="Name one primary color.", mode="single", batch=False,
             image=False, model="Qwen/Qwen3.5-0.8B", cached=True, device="cuda:0"):
    graph = {
        "1": {"class_type": "QwenModel", "inputs": {
            "model": model, "backend": "auto", "quantization": "auto",
            "device": device, "mode": mode}},
        "2": {"class_type": "QwenBatch" if batch else "QwenGenerate", "inputs": {
            "model": ["1", 0], "prompt": prompt, "prefix": "assistant",
            "max_tokens": 32, "temperature": 0.0, "prefix_cache": cached}},
    }
    if image:
        graph["3"] = {"class_type": "LoadImage", "inputs": {"image": "qwen-red.png"}}
        graph["2"]["inputs"]["images"] = ["3", 0]
    return graph
