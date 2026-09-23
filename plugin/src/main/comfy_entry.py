import os
import runpy
import sys
from pathlib import Path
from .ipv4 import enable

enable()
root = Path(sys.argv.pop(1))
sys.path.insert(0, str(root))
os.chdir(root)
runpy.run_path(str(root / "main.py"), run_name="__main__")
