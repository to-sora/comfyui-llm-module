import subprocess
from pathlib import Path
import yaml
from .api import ready

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "plugin"


def configure(model="Qwen/Qwen3.5-0.8B"):
    path = APP / "config/config.yaml"
    cfg = yaml.safe_load(path.read_text())
    cfg["startup_models"] = [{"model": model, "mode": "single"}]
    path.write_text(yaml.safe_dump(cfg, allow_unicode=True))
    data = APP / "data"
    data.mkdir(exist_ok=True)
    with (data / "comfy.log").open("w") as log:
        process = subprocess.Popen(["bash", str(APP / "start.sh")],
                                   cwd=ROOT, stdout=log, stderr=log)
    print(f"ComfyUI launcher PID: {process.pid}; https://127.0.0.1:8188")
    print("Self-signed certificate: manual browser trust / 自簽憑證：瀏覽器手動信任")
    ready(process=process)


if __name__ == "__main__":
    configure()
