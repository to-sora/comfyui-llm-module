import numpy as np
from PIL import Image, ImageDraw
from client import call, session, tool, wait, upload, picture, save

sid = session("Acceptance · Inpaint & img2img")
call(f"/session/{sid}/settings", {"width": 512, "height": 512, "steps": 10, "scheduler": "normal"})
src = Image.new("RGBA", (513, 505), (210, 230, 250, 255))
ImageDraw.Draw(src).rectangle((150, 150, 360, 350), fill=(240, 60, 50, 255))
source = upload(sid, src)["id"]
mask = Image.new("L", src.size)
ImageDraw.Draw(mask).ellipse((170, 170, 340, 330), fill=255)
mask_id = upload(sid, mask, True)["id"]
inpaint = tool(sid, "image_gen_sdxl_inpaint", {"source": source, "mask": mask_id,
    "prompt": "A shiny blue sphere on a pale blue table", "seed": 71})
img = tool(sid, "image_gen_sdxl_image", {"source": source,
    "prompt": "A red square on a pale blue background, minimalist art", "denoise": 0.35, "seed": 72})
assert "error" not in inpaint and "error" not in img, [inpaint, img]
batch = tool(sid, "sent_all_pending")
result, state = wait(sid, "batches", batch["id"])
assert result["status"] == "done", [(j["id"], j.get("error")) for j in state["jobs"]]
job = next(j for j in state["jobs"] if j["id"] == inpaint["id"])
out = picture(sid, job["image"])
original, actual, m = np.asarray(src), np.asarray(out), np.asarray(mask)
assert out.size == src.size
assert np.array_equal(original[m == 0], actual[m == 0])
assert np.any(original[m > 0] != actual[m > 0])
save("workflows", {"session": sid, "inpaint": job["image"], "size": out.size,
    "unmasked_changed_pixels": int(np.count_nonzero(np.any(original != actual, axis=2) & (m == 0))),
    "masked_changed_pixels": int(np.count_nonzero(np.any(original != actual, axis=2) & (m > 0))),
    "image_to_image": result["images"][1], "status": "PASS"})
print("Image-to-image and inpaint PASS; unmasked pixels identical")
