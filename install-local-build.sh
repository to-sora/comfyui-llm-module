#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
mkdir -p .local-tool
command -v python3 >/dev/null || {
  echo 'Python required: Useful_shell_script/install_python.sh / 需要 Python 環境'
  exit 1
}
if [[ ! -x .local-tool/venv/bin/python ]]; then
  python3 -m venv --without-pip .local-tool/venv
fi
