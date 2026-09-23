#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
source ./env.sh
if [[ ! -x venv/bin/python ]]; then
  python3 -m venv --system-site-packages venv
fi
venv/bin/python src/main/pip_ipv4.py install --retries 0 --timeout 15 \
  torch==2.8.0 torchvision==0.23.0 --index-url https://download.pytorch.org/whl/cpu
venv/bin/python src/main/pip_ipv4.py install --retries 0 --timeout 15 -r requirements.txt
