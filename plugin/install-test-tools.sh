#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
source ./env.sh
.local-tool-app/venv/bin/python src/main/pip_ipv4.py install marionette-driver==3.7.1
