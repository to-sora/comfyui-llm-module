#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
source ./env.sh
cd ..
exec plugin/.local-tool-app/venv/bin/python -m plugin.src.main.launcher "$@"
