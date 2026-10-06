from pathlib import Path
import yaml

APP = Path(__file__).resolve().parents[2]
DATA = APP / "data"


def read(name="config.yaml"):
    return yaml.safe_load((APP / "config" / name).read_text())


def prepare():
    for folder in ("assets", "thumbs", "tls", "tmp", "cache"):
        (DATA / folder).mkdir(parents=True, exist_ok=True)
