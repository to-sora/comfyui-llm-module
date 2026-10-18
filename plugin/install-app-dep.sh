#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
source ./env.sh
export COMFY_VENV="$QWEN_APP/.local-tool-app/venv"
[[ -x "$COMFY_VENV/bin/python" ]] || "$COMFY_BOOTSTRAP_PYTHON" -m venv "$COMFY_VENV"
[[ -f "$QWEN_APP/../../comfyui/requirements.txt" ]] || { echo 'Existing ComfyUI installation required'; exit 1; }
"$COMFY_VENV/bin/python" src/main/pip_ipv4.py install -r "$QWEN_APP/../../comfyui/requirements.txt"
"$COMFY_VENV/bin/python" src/main/pip_ipv4.py install -r requirements.txt
cd ..
"$COMFY_VENV/bin/python" -m plugin.src.main.install_image_model
