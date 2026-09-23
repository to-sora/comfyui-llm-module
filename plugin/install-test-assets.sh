#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")/.."
source plugin/env.sh
plugin/venv/bin/python - <<'PY'
from plugin.src.main.ipv4 import enable
enable()
from huggingface_hub import snapshot_download
snapshot_download("Qwen/Qwen3.5-0.8B", max_workers=2,
                  allow_patterns=["*.json", "*.txt", "*.jinja"])
PY
