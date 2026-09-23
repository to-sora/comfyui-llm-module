#!/usr/bin/env bash
set -euo pipefail
app="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
source "$app/environment.sh"
python="$app/.local-tool-app/venv/bin/python"
comfy="$app/.local-tool-app/ComfyUI"
bash "$app/install-local-app-build.sh" core
if [ ! -d "$comfy/.git" ]; then
  git clone -4 --depth 1 https://github.com/Comfy-Org/ComfyUI.git "$comfy"
fi
"$python" "$app/src/main/constraints.py"
"$python" "$app/src/main/pip_ipv4.py" install \
  -c "$app/.local-tool-app/constraints.txt" -r "$comfy/requirements.txt"
"$python" "$app/src/main/setup_comfy.py"
