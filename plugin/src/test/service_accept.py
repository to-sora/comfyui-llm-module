import json
from pathlib import Path
import torch
from PIL import Image
from plugin.src.main.settings import APP, environment
from plugin.colab.api import execute, free_models, ready, request
from plugin.colab.workflow import workflow
from plugin.src.test.service_support import service


def main():
    environment()
    torch.set_num_threads(2)
    with service() as (model, process):
        ready(90, process)
        assert any(m["prefix_bytes"] > 0 for m in request("/qwen/status")["models"])
        def graph(**kwargs):
            return workflow(model=model, device="cpu", **kwargs)
        first = execute(graph())
        assert first == execute(graph(cached=False)) and any(first)
        free_models()
        assert execute(graph()) == first
        for mode in ["single", "concurrent"]:
            prompts = json.dumps(["Name a color."] * 8)
            batch = execute(graph(prompt=prompts, mode=mode, batch=True))
            assert len(batch) == 8 and len(set(batch)) == 1
        assert any(m["peak_active"] == 2 for m in request("/qwen/status")["models"])
        path = APP / "data/input/qwen-red.png"
        Image.new("RGB", (64, 32), (255, 0, 0)).save(path)
        assert execute(graph(image=True))
        assert execute(graph()) == first
        last = graph()
        last["4"] = {"class_type": "QwenUnload", "inputs": {"after": ["2", 0]}}
        execute(last)
        assert all(not m["loaded"] for m in request("/qwen/status")["models"])
        assert process.poll() is None
        proof = {"result": "PASS", "service": "ComfyUI HTTPS API", "device": "cpu",
                 "weights": "random Qwen3.5 fixture", "mocks": [],
                 "startup_prefix_ram": True, "cache_equivalence": True,
                 "single_and_concurrent": True, "native_free_and_reload": True,
                 "vision_tensor_path": True, "unload_node": True}
    folder = APP.parent / "fan-out"
    folder.mkdir(exist_ok=True)
    (folder / "cpu-service-result.json").write_text(json.dumps(proof, indent=2))
    print(json.dumps(proof))


if __name__ == "__main__":
    main()
