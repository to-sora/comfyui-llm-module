#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
mkdir -p .local-tool
bootstrap_python="${COMFY_BOOTSTRAP_PYTHON:-$HOME/cache/opt/python-3.13.11/bin/python3.13}"
[[ -x "$bootstrap_python" ]] || {
  echo 'Python required: Useful_shell_script/install_python.sh / 需要 Python 環境'
  exit 1
}
printf 'Using Python / 使用 Python: %s\n' "$bootstrap_python"
