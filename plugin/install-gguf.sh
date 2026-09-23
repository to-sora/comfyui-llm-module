#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
source ./env.sh
bash .local-tool-app/install-local-app-build.sh
export PATH="$QWEN_APP/.local-tool-app/venv/bin:$QWEN_APP/venv/bin:$PATH"
export CMAKE_ARGS="-DGGML_CUDA=${QWEN_CUDA:-ON}"
venv/bin/python src/main/pip_ipv4.py install llama-cpp-python==0.3.35
