#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")/.."
export PYTHONDONTWRITEBYTECODE=1
exec server/.local-tool-app/venv/bin/python -m server.src.main.launcher "$@"
