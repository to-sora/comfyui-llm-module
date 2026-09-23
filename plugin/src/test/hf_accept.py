import json
import torch
from PIL import Image
from plugin.src.main.ipv4 import enable
from plugin.src.main.settings import environment, options
from plugin.src.main.hf_engine import HFEngine

enable()
environment()
torch.set_num_threads(2)
cfg = options("Qwen/Qwen3.5-0.8B", device="cpu")
engine = HFEngine(cfg)
try:
    engine.warm()
    args = ("Name one primary color.", cfg["prefixes"]["assistant"], None, 16, 0.0)
    cached = engine.generate(*args)
    cold = engine.generate(*args, prefix_cache=False)
    assert cached.strip() and cached == cold, (cached, cold)
    assert engine.cache.bytes > 0 and engine.cache.hits > 0
    red = Image.new("RGB", (224, 224), (255, 0, 0))
    vision = engine.generate("Name the image's main color in English.",
                             cfg["prefixes"]["assistant"], [red], 16, 0.0)
    assert "red" in vision.lower(), vision
    assert engine.generate(*args) == cached, "Vision/text state isolation"
    print(json.dumps({"CPU_inference": cached, "vision": vision,
                      "prefix_bytes": engine.cache.bytes,
                      "prefix_hits": engine.cache.hits, "cache_equivalence": True}))
finally:
    engine.close()
