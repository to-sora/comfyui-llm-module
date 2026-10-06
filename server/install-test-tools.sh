#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
export PIP_CACHE_DIR="$PWD/.local-tool-app/pip-cache" TMPDIR="$PWD/data/tmp"
.local-tool-app/venv/bin/python src/main/pip_ipv4.py install marionette-driver==3.7.1
test -x "$HOME/UAT-firefox/firefox/firefox" || {
  echo 'Install Firefox in ~/UAT-firefox / 請安裝 Firefox 至 ~/UAT-firefox'; exit 1;
}
