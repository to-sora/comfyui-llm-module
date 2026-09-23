#!/usr/bin/env bash
set -euo pipefail
if [ "$(id -u)" -ne 0 ]; then
  echo 'Run with sudo / 請以 sudo 執行' >&2
  exit 1
fi
apt-get -o Acquire::ForceIPv4=true update
apt-get -o Acquire::ForceIPv4=true install -y \
  build-essential make cmake ninja-build git openssl python3-venv
