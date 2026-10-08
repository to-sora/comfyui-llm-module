#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")/.."
source ./env.sh
QWEN_KERNEL_PYTHON="$QWEN_APP/.local-tool-app/venv/bin/python"
if ! command -v nvcc >/dev/null; then
  printf '%s\n' 'CUDA nvcc is required. This installer does not change system packages.' >&2
  exit 1
fi
"$QWEN_KERNEL_PYTHON" src/main/pip_ipv4.py install --no-deps \
  wheel==0.48.0 ninja==1.11.1.4 setuptools==78.1.0 packaging==26.3 \
  fla-core==0.5.2 flash-linear-attention==0.5.2
mkdir -p .local-dep/wheels
export CAUSAL_CONV1D_FORCE_BUILD=TRUE
export MAX_JOBS="${QWEN_KERNEL_BUILD_JOBS:-4}"
timeout --signal=TERM --kill-after=10s 1200 \
  "$QWEN_KERNEL_PYTHON" src/main/pip_ipv4.py wheel --no-deps --no-build-isolation \
  --wheel-dir .local-dep/wheels causal-conv1d==1.7.0
"$QWEN_KERNEL_PYTHON" src/main/pip_ipv4.py install --no-deps --no-index \
  --find-links .local-dep/wheels causal-conv1d==1.7.0
