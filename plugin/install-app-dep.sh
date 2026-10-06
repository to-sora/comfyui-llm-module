#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
source ./env.sh
export COMFY_VENV="$QWEN_APP/.local-tool-app/venv"
bash "$QWEN_APP/../../civit_script/install.sh"
"$COMFY_VENV/bin/python" src/main/pip_ipv4.py install -r requirements.txt
target="$QWEN_APP/../../comfyui/custom_nodes/comfyui-llm-module"
mkdir -p -- "$(dirname -- "$target")"
if [[ ! -e "$target" ]]; then
  ln -s "$(dirname -- "$QWEN_APP")" "$target"
fi
