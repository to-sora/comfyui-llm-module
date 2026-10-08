#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
app_python="${COMFY_BOOTSTRAP_PYTHON:-$HOME/cache/opt/python-3.13.11/bin/python3.13}"
[[ -x "$app_python" ]] || { echo 'Python required / 需要 Useful_shell_script Python'; exit 1; }
mkdir -p .local-tool-app data/tmp data/cache
export TMPDIR="$PWD/data/tmp" PIP_CACHE_DIR="$PWD/.local-tool-app/pip-cache"
[[ -x .local-tool-app/venv/bin/python ]] || "$app_python" -m venv .local-tool-app/venv
.local-tool-app/venv/bin/python src/main/pip_ipv4.py install -r requirements.txt
.local-tool-app/venv/bin/python install-fonts.py
