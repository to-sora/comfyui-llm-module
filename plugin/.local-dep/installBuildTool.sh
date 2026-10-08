#!/usr/bin/env bash
set -euo pipefail
# Administrator-only preparation; the coding agent must not run this script.
sudo apt-get update
sudo apt-get install -y build-essential
printf '%s\n' 'Use the existing CUDA 13 toolkit with nvcc for the local build.'
