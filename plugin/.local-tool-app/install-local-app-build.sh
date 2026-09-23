#!/usr/bin/env bash
set -euo pipefail
app="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
source "$app/environment.sh"
python_cmd="${QWEN_PYTHON:-python3}"
if ! command -v "$python_cmd" >/dev/null; then
  echo 'Python required: to-sora/Useful_shell_script install_python.sh' >&2
  exit 1
fi
venv="$app/.local-tool-app/venv"
if [ ! -x "$venv/bin/python" ]; then
  "$python_cmd" -m venv --system-site-packages "$venv"
fi
if ! "$venv/bin/python" -c 'import torch' 2>/dev/null; then
  "$venv/bin/python" "$app/src/main/pip_ipv4.py" install \
    torch==2.11.0 torchvision==0.26.0 \
    --index-url "https://download.pytorch.org/whl/${QWEN_TORCH_INDEX:-cpu}"
fi
"$venv/bin/python" "$app/src/main/constraints.py"
profile="${1:-core}"
case "$profile" in
  core|bnb|gptq|hqq|quanto|compressed|torchao|gguf|test) ;;
  *) echo 'Unknown dependency profile / 相依套件類型錯誤' >&2; exit 2 ;;
esac
if [ "$profile" = gguf ]; then
  export CMAKE_ARGS="-DGGML_CUDA=${QWEN_CUDA:-ON}"
fi
"$venv/bin/python" "$app/src/main/pip_ipv4.py" install \
  -c "$app/.local-tool-app/constraints.txt" -r "$app/requirements-$profile.txt"
