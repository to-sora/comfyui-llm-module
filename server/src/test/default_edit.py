import json
from PIL import Image, ImageDraw
from .client import call, session, tool, wait, upload, ROOT

sid = session("Default edit acceptance")
source = Image.new("RGB", (600, 400), "white")
ImageDraw.Draw(source).rectangle((160, 120, 390, 280), fill="red")
image = upload(sid, source)["id"]
job = tool(sid, "image_gen_sdxl_image", {"source": image,
    "prompt": "A blue square on a clean white background, simple flat illustration"})
batch = tool(sid, "sent_all_pending")
result, state = wait(sid, "batches", batch["id"])
assert result["status"] == "done", state["jobs"]
picture = next(i for i in state["images"] if i["id"] in result["images"])
settings = picture["settings"]
assert settings["denoise"] == .5 and settings["cfg"] == 5.5
assert abs(picture["width"] / picture["height"] - 1.5) < .01
assert 1_000_000 <= picture["width"] * picture["height"] <= 1_100_000
assert picture["parents"] == [image]
proof = {"status": "PASS", "source_size": source.size, "output_size": [picture["width"], picture["height"]],
         "strength": settings["denoise"], "seed": settings["seed"], "cfg": settings["cfg"],
         "source": image, "image": picture["id"], "session": sid}
(ROOT / "fan-out/studio-engine/default-edit.json").write_text(json.dumps(proof, indent=2))
print(json.dumps(proof), flush=True)
