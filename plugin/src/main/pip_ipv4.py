import runpy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ipv4 import enable

enable()
runpy.run_module("pip", run_name="__main__")
