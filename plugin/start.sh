#!/usr/bin/env bash
set -euo pipefail
app="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
source "$app/environment.sh"
exec "$app/.local-tool-app/venv/bin/python" "$app/src/main/launcher.py" "$@"
