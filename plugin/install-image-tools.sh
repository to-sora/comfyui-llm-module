#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")/.."
plugin/.local-tool-app/venv/bin/python plugin/src/main/pip_ipv4.py install onnxruntime==1.24.4
plugin/.local-tool-app/venv/bin/python -m plugin.src.main.install_image_model
