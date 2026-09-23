#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")/.."
source ./env.sh
if [[ ! -x .local-tool-app/venv/bin/python ]]; then
  python3 -m venv .local-tool-app/venv
fi
.local-tool-app/venv/bin/python src/main/pip_ipv4.py install cmake==4.0.3 ninja==1.11.1.4
