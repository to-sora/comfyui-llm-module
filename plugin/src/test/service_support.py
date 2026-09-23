import os
import subprocess
import tempfile
from contextlib import contextmanager
from pathlib import Path
import yaml
from plugin.src.main.settings import APP
from plugin.src.test.tensor_support import fixture


@contextmanager
def service():
    cfg_path = APP / "config/config.yaml"
    original = cfg_path.read_bytes()
    with tempfile.TemporaryDirectory(dir=APP / "data/tmp") as folder:
        model = fixture(Path(folder) / "model")
        cfg = yaml.safe_load(original)
        cfg["startup_models"] = [{"model": model, "device": "cpu"}]
        process = None
        with (APP / "data/comfy-test.log").open("w") as log:
            try:
                cfg_path.write_text(yaml.safe_dump(cfg))
                env = dict(os.environ, OMP_NUM_THREADS="2", MKL_NUM_THREADS="2")
                process = subprocess.Popen([str(APP / "start.sh"), "--cpu"],
                                           env=env, stdout=log, stderr=log)
                yield model, process
            finally:
                if process is not None and process.poll() is None:
                    subprocess.run([str(APP / "start.sh"), "--stop"], check=True)
                    process.wait(timeout=15)
                cfg_path.write_bytes(original)
