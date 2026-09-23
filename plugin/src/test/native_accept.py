import json
import sys
import tempfile
import weakref
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import torch
from plugin.src.main.settings import APP, environment, options

environment()
comfy = Path(sys.argv[1]) if len(sys.argv) > 1 else APP / ".local-tool-app/ComfyUI"
sys.path.insert(0, str(comfy.resolve()))
import comfy.cli_args
comfy.cli_args.args.cpu = True
from comfy import model_management as mm
from plugin.src.main.runtime import get_handle
from plugin.src.test.tensor_support import fixture


def main():
    torch.set_num_threads(2)
    with tempfile.TemporaryDirectory(dir=APP / "data/tmp") as folder:
        model = fixture(Path(folder) / "model")
        handle = get_handle(options(model, device="cpu"))
        args = ("Name a color.", "assistant", None, 4, 0.0)
        try:
            text = handle.generate(*args)
            assert handle.patcher in mm.loaded_models()
            assert handle.pool.status()["prefix_hits"] == 1
            weight = weakref.ref(handle.pool.engines[0].model)
            mm.unload_all_models()
            assert not handle.pool.status()["loaded"]
            assert weight() is None, "Native unload retains model weights"
            assert handle.generate(*args) == text
            mm.unload_all_models()
            parallel = get_handle(options(model, device="cpu", mode="concurrent"))
            with ThreadPoolExecutor(4) as executor:
                results = list(executor.map(lambda _: parallel.generate(*args), range(8)))
            assert results == [text] * 8
            state = parallel.pool.status()
            assert state["peak_active"] == 2 and state["active"] == 0
            mm.unload_all_models()
            assert not parallel.pool.status()["loaded"]
            print(json.dumps({"native_unload_reload": "PASS", "queued_requests": 8,
                              "peak_active": state["peak_active"], "device": "cpu",
                              "weights": "random Qwen3.5 fixture", "mocks": []}))
        finally:
            mm.unload_all_models()


if __name__ == "__main__":
    main()
