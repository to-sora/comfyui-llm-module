#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
mkdir -p .local-tool-app/templates
curl -4 -fL https://huggingface.co/google/gemma-4-E2B-it/resolve/main/chat_template.jinja \
  -o .local-tool-app/templates/gemma4.jinja
