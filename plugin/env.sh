#!/usr/bin/env bash
QWEN_APP="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
export COMFY_BOOTSTRAP_PYTHON="${COMFY_BOOTSTRAP_PYTHON:-$HOME/cache/opt/python-3.13.11/bin/python3.13}"
export HF_HOME="$QWEN_APP/data/hf"
export HF_HUB_CACHE="$HF_HOME/hub"
export HUGGINGFACE_HUB_CACHE="$HF_HUB_CACHE"
export TORCH_HOME="$QWEN_APP/data/torch"
export XDG_CACHE_HOME="$QWEN_APP/data/cache"
export PIP_CACHE_DIR="$QWEN_APP/.local-tool-app/pip-cache"
export TMPDIR="$QWEN_APP/data/tmp"
export HF_HUB_DISABLE_XET=1
export HF_HUB_DISABLE_TELEMETRY=1
export HF_HUB_DISABLE_PROGRESS_BARS=1
export TQDM_DISABLE=1
export CUDA_CACHE_PATH="$QWEN_APP/data/cuda"
export TRITON_CACHE_DIR="$QWEN_APP/data/triton"
export TORCHINDUCTOR_CACHE_DIR="$QWEN_APP/data/inductor"
mkdir -p "$HF_HOME" "$TORCH_HOME" "$XDG_CACHE_HOME" "$PIP_CACHE_DIR" "$TMPDIR"
