#!/usr/bin/env bash
set -euo pipefail
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$root/.local-tool"
exec bash "$root/plugin/install-local-app-build.sh" core
