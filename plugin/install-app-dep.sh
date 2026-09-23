#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
source ./env.sh
if [[ ! -x venv/bin/python ]]; then
  python3 -m venv --system-site-packages venv
fi
venv/bin/python src/main/pip_ipv4.py install -r requirements.txt
if [[ ! -d .local-tool-app/ComfyUI/.git ]]; then
  git clone -4 --depth 1 https://github.com/Comfy-Org/ComfyUI.git .local-tool-app/ComfyUI
fi
if [[ ! -f .local-tool-app/ComfyUI/requirements.txt ]]; then
  git -C .local-tool-app/ComfyUI fetch -4 --depth 1 origin master
  git -C .local-tool-app/ComfyUI checkout -f FETCH_HEAD
fi
venv/bin/python src/main/pip_ipv4.py install -c requirements.txt -r .local-tool-app/ComfyUI/requirements.txt
target="$QWEN_APP/.local-tool-app/ComfyUI/custom_nodes/comfyui-llm-module"
if [[ ! -e "$target" ]]; then
  ln -s "$(dirname -- "$QWEN_APP")" "$target"
fi
venv/bin/python src/main/pip_ipv4.py install -r requirements.txt
