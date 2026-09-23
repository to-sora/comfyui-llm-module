#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
source ./env.sh
case "${1:-bnb}" in
  bnb) packages=(bitsandbytes==0.50.2) ;;
  gptq|awq) packages=(gptqmodel==7.5.0 optimum==2.3.0) ;;
  hqq) packages=(hqq==0.2.8.post1) ;;
  quanto) packages=(optimum-quanto==0.2.7) ;;
  compressed) packages=(compressed-tensors==0.19.0) ;;
  *) echo 'Profiles / 設定: bnb gptq awq hqq quanto compressed'; exit 1 ;;
esac
venv/bin/python src/main/pip_ipv4.py install -c requirements.txt "${packages[@]}"
