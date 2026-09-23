#!/usr/bin/env bash
set -euo pipefail
sudo apt-get -o Acquire::ForceIPv4=true update
sudo apt-get -o Acquire::ForceIPv4=true install -y build-essential cmake ninja-build git openssl python3-venv
