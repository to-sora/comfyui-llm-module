#!/usr/bin/env bash
QWEN_APP="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
export HF_HOME="$QWEN_APP/data/hf"
export TORCH_HOME="$QWEN_APP/data/torch"
export XDG_CACHE_HOME="$QWEN_APP/data/cache"
export PIP_CACHE_DIR="$QWEN_APP/data/pip"
export TMPDIR="$QWEN_APP/data/tmp"
export HF_HUB_DISABLE_XET=1
export HF_HUB_DISABLE_TELEMETRY=1
mkdir -p "$HF_HOME" "$TORCH_HOME" "$XDG_CACHE_HOME" "$PIP_CACHE_DIR" "$TMPDIR"
