#!/usr/bin/env bash
app="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
export HF_HOME="$app/data/hf" TORCH_HOME="$app/data/torch"
export XDG_CACHE_HOME="$app/data/cache" TMPDIR="$app/data/tmp"
export PIP_CACHE_DIR="$app/.local-tool-app/pip-cache"
export HF_HUB_DISABLE_XET=1 HF_HUB_DISABLE_TELEMETRY=1
export PIP_DISABLE_PIP_VERSION_CHECK=1
export PATH="$app/.local-tool-app/venv/bin:$PATH"
mkdir -p "$HF_HOME" "$TORCH_HOME" "$XDG_CACHE_HOME" "$TMPDIR" "$PIP_CACHE_DIR"
