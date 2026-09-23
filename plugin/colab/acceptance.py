import json
from pathlib import Path
from .api import execute, free_models, ready, request
from .workflow import workflow

ROOT = Path(__file__).resolve().parents[2]


def main():
    ready()
    initial = request("/qwen/status")
    assert any(m["prefix_bytes"] > 0 for m in initial["models"]), "Startup RAM prefill"
    first = execute(workflow())
    cold = execute(workflow(cached=False))
    assert first == cold and any(t.strip() for t in first), "Cached/uncached inference"
    loaded = request("/qwen/status")
    assert any(m["prefix_hits"] > 0 for m in loaded["models"]), "Prefix reuse"
    assert loaded["cuda_allocated"] > 1024**2, "GPU model allocation"
    freed = free_models()
    released = loaded["cuda_allocated"] - freed["cuda_allocated"]
    assert released > 1024**2, "GPU weights released through ComfyUI /free"
    assert any(t.strip() for t in execute(workflow())), "Reload after /free"
    single = execute(workflow(prompt='["Name a color.","Name a shape."]', batch=True))
    assert len(single) == 2 and all(t.strip() for t in single)
    parallel = execute(workflow(prompt='["Name a color.","Name a shape."]',
                                mode="concurrent", batch=True))
    assert len(parallel) == 2 and all(t.strip() for t in parallel)
    concurrent = request("/qwen/status")
    assert any(m["peak_active"] == 2 for m in concurrent["models"]), "Concurrent workers"
    free_models()
    from PIL import Image
    path = ROOT / "plugin/data/input/qwen-red.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (224, 224), (255, 0, 0)).save(path)
    vision = execute(workflow(prompt="Name the image's main color in English.", image=True))
    assert "red" in " ".join(vision).lower(), vision
    graph = workflow(prompt="Name one shape.")
    graph["4"] = {"class_type": "QwenUnload", "inputs": {"after": ["2", 0]}}
    execute(graph)
    state = request("/qwen/status")
    assert all(not m["loaded"] for m in state["models"]), "Unload node"
    proof = {"result": "PASS / 通過", "model": "Qwen/Qwen3.5-0.8B",
             "inference": first, "vision": vision, "released_gpu_bytes": released,
             "startup_prefix_ram": True, "cache_equivalence": True,
             "single_and_concurrent": True, "native_free_and_reload": True}
    folder = ROOT / "fan-out"
    folder.mkdir(exist_ok=True)
    (folder / "colab-result.json").write_text(json.dumps(proof, ensure_ascii=False, indent=2))
    print(json.dumps(proof, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
