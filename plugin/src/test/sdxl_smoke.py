import io
import json
import time
from pathlib import Path
from urllib.parse import urlencode

import numpy as np
from PIL import Image
from .api_client import execute, request
from .sdxl_graph import graph


def main():
    started = time.monotonic()
    prompt_id, outputs = execute(graph())
    item = outputs["7"]["images"][0]
    content = request("/view?" + urlencode(item), binary=True)
    picture = Image.open(io.BytesIO(content))
    assert picture.size == (1024, 1024), picture.size
    deviation = float(np.asarray(picture.convert("RGB")).std())
    assert deviation > 5, "Generated image is blank"
    folder = Path(__file__).resolve().parents[3] / "fan-out"
    folder.mkdir(exist_ok=True)
    (folder / "sdxl-baseline.png").write_bytes(content)
    evidence = {"api": "ComfyUI HTTPS", "checkpoint": "sd_xl_base_1.0.safetensors",
                "prompt_id": prompt_id, "size": picture.size,
                "pixel_std": deviation, "seconds": time.monotonic() - started,
                "status": "API generation passed / API 出圖通過"}
    (folder / "sdxl-baseline.json").write_text(json.dumps(evidence, indent=2))
    print(json.dumps(evidence))


if __name__ == "__main__":
    main()
