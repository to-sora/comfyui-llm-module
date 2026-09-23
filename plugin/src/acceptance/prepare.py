import json
import sys
from pathlib import Path

MAIN = Path(__file__).resolve().parents[1] / "main"
sys.path.insert(0, str(MAIN))
from ipv4 import enable
from settings import APP, DATA, configure_paths, read_config

enable()
configure_paths()
import torch
import yaml
from huggingface_hub import snapshot_download
from PIL import Image

if not torch.cuda.is_available():
    raise RuntimeError("Colab GPU runtime required / 驗收需要 Colab GPU runtime")
model = sys.argv[1] if len(sys.argv) > 1 else "Qwen/Qwen3.5-0.8B"
snapshot_download(model, cache_dir=str(DATA / "hf"),
    allow_patterns=["*.json", "*.safetensors", "*.model", "*.txt", "*.jinja"])
config = read_config()
config["startup_models"] = [{"model": model, "mode": "single"}]
config["device"] = "cuda:0"
config["workers"] = 2
(APP / "config/config.yaml").write_text(yaml.safe_dump(config), encoding="utf-8")
Image.new("RGB", (224, 224), (255, 0, 0)).save(DATA / "input/red.png")
(DATA / "acceptance-model.json").write_text(json.dumps({"model": model}))
print("GPU / 顯示卡:", torch.cuda.get_device_name(0))
print("Python / PyTorch / CUDA:", sys.version.split()[0], torch.__version__, torch.version.cuda)
