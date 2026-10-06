#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
source ./env.sh
bash .local-tool-app/install-local-app-build.sh
export PATH="$QWEN_APP/.local-tool-app/venv/bin:$PATH"
export CMAKE_ARGS="-DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=89 -DGGML_NATIVE=OFF"
export CMAKE_BUILD_PARALLEL_LEVEL=8
timeout -k 10 1200 .local-tool-app/venv/bin/python src/main/pip_ipv4.py \
    install llama-cpp-python==0.3.36
