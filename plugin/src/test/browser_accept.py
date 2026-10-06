import json
import time
from pathlib import Path
from PIL import Image
from .browser_session import browser
from .browser_actions import open_app, run_graph, fit
from .model_cases import TOOL, user
from .sdxl_graph import graph as sdxl
from ..main.gateway_graph import graph


def main():
    started = time.monotonic()
    root = Path(__file__).resolve().parents[3]
    out = root / "fan-out"
    Image.new("RGB", (256, 256), "blue").save(root / "plugin/data/input/uat-blue.png")
    body = {"model": "Qwen3.5-9B", "kv_quantization": "hqq_4", "max_tokens": 96,
            "parallel_tool_calls": False,
            "messages": [user("What is 17 + 25? Reply with only the number.")]}
    proof = {}
    with browser() as b:
        open_app(b)
        def chat(workflow):
            data = run_graph(b, workflow, 2)
            fit(b)
            return json.loads(data["text"][0])["choices"][0]["message"]
        proof["text"] = chat(graph(body))["content"]
        assert proof["text"].strip() == "42"
        vision = graph(dict(body, messages=[user("What color is this image? Reply with one word.")]))
        vision["3"] = {"class_type": "LoadImage", "inputs": {"image": "uat-blue.png"}}
        vision["2"]["inputs"]["images"] = ["3", 0]
        proof["image"] = chat(vision)["content"]
        assert "blue" in proof["image"].lower()
        fit(b)
        (out / "gui-image.png").write_bytes(b.screenshot(format="binary"))
        tool = chat(graph(dict(body, tools=[TOOL], messages=[user("Use get_weather for Hong Kong.")])))
        proof["tool"] = tool["tool_calls"][0]["function"]
        assert json.loads(proof["tool"]["arguments"])["city"] == "Hong Kong"
        (out / "gui-tool.png").write_bytes(b.screenshot(format="binary"))
        proof["sdxl"] = run_graph(b, sdxl(seed=int(time.time())), 7)["images"][0]
        proof["after_sdxl"] = chat(graph(body))["content"]
        assert proof["after_sdxl"].strip() == "42"
        for name, width, height in [("wide", 1440, 1000), ("portrait", 900, 1400), ("large", 1920, 1200)]:
            b.set_window_rect(width=width, height=height)
            b.execute_script("window.comfyAPI.app.app.graph._nodes.forEach((n,i)=>"
                "{n.pos=arguments[0] ? [100,100+i*680] : [100+i*500,140]})", [width < height], sandbox=None)
            fit(b)
            (out / f"gui-{name}.png").write_bytes(b.screenshot(format="binary"))
    proof.update(status="PASS", seconds=time.monotonic() - started)
    (out / "gui.json").write_text(json.dumps(proof, indent=2))
    print(json.dumps(proof))


if __name__ == "__main__":
    main()
