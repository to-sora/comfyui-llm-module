#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
source ./env.sh
if [[ ! -x venv/bin/python ]]; then
  python3 -m venv --system-site-packages venv
fi
venv/bin/python src/main/pip_ipv4.py install -r requirements.txt
if [[ ! -d .local-tool-app/ComfyUI/.git ]]; then
  git clone -4 https://github.com/Comfy-Org/ComfyUI.git .local-tool-app/ComfyUI
fi
venv/bin/python src/main/pip_ipv4.py install -r .local-tool-app/ComfyUI/requirements.txt
target="$QWEN_APP/.local-tool-app/ComfyUI/custom_nodes/comfyui-llm-module"
if [[ ! -e "$target" ]]; then
  ln -s "$(dirname -- "$QWEN_APP")" "$target"
fi
venv/bin/python src/main/pip_ipv4.py install -r requirements.txt
