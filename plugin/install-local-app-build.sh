#!/usr/bin/env bash
set -euo pipefail
app="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec bash "$app/.local-tool-app/install-local-app-build.sh" "${1:-core}"
