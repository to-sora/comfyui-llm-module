import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parent
cases = [("workflow_accept.py",), ("jobs_accept.py",)] + [
    ("chat_accept.py", model) for model in ("Qwen3.5-9B-gguf",
    "Qwen3.8-27B-OBLITERATED", "Qwen3.8-27B", "gemma-4-E2B")]
for case in cases:
    print("TEST", *case, flush=True)
    subprocess.run([sys.executable, str(root / case[0]), *case[1:]], check=True)
