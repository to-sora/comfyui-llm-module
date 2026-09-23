from importlib.metadata import version, PackageNotFoundError
from pathlib import Path

app = Path(__file__).resolve().parents[2]
lines = ["transformers==5.17.0"]
for package in ("torch", "torchvision", "torchaudio", "numpy"):
    try:
        lines.append(f"{package}=={version(package)}")
    except PackageNotFoundError:
        pass
(app / ".local-tool-app/constraints.txt").write_text(
    "\n".join(lines) + "\n", encoding="utf-8")
