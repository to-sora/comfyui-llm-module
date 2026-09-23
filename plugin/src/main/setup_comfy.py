from pathlib import Path
from settings import APP, DATA, ROOT, configure_paths

configure_paths()
for name in ("comfy/custom_nodes", "input", "output", "user", "tls"):
    (DATA / name).mkdir(parents=True, exist_ok=True)
target = DATA / "comfy/custom_nodes/comfyui-llm-module"
if not target.exists():
    target.symlink_to(ROOT, target_is_directory=True)
elif target.resolve() != ROOT:
    raise RuntimeError(f"Existing extension path belongs to {target.resolve()}")
from tls import certificate
certificate()
print("Installed / 安裝完成:", APP)
