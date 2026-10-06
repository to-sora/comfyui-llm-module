from PIL import Image, ImageDraw
from client import call, session, tool, upload, wait, picture, save

sid = session("Acceptance · CPU edits")
src = Image.new("RGBA", (512, 512), "white")
ImageDraw.Draw(src).rectangle((128, 128, 384, 384), fill="red")
base = upload(sid, src)["id"]
definitions = call("/bootstrap")["edits"]
jobs = []
for operation in definitions:
    params = {}
    if operation == "text":
        params = {"text": "Hello 圖片", "font": "Noto Sans CJK TC", "bold": True,
                  "italic": True, "size": 48, "color": "#0011ff", "indent": 10}
    if operation == "overlay":
        params = {"overlay": base, "x": 20, "opacity": 0.5}
    job = tool(sid, "image_edit_" + operation, {"source": base, "params": params})
    assert "error" not in job, job
    jobs.append((operation, job["id"]))
batch = tool(sid, "sent_all_pending")
result, state = wait(sid, "batches", batch["id"])
assert result["status"] == "done", [(j["args"]["operation"], j.get("error")) for j in state["jobs"]]
results = {j["args"]["operation"]: j["image"] for j in state["jobs"]}
removed = picture(sid, results["remove_background"])
assert removed.getpixel((0, 0))[3] == 0
assert removed.getpixel((200, 200))[3] == 255
large = tool(sid, "image_edit_resize", {"source": base, "width": 4096, "height": 4096})
b = tool(sid, "sent_all_pending")
r, _ = wait(sid, "batches", b["id"])
assert picture(sid, r["images"][0]).size == (4096, 4096)
invalid = tool(sid, "image_edit_resize", {"source": base, "width": 4097, "height": 4096})
assert "error" in invalid
save("cpu", {"session": sid, "operations": list(results), "count": len(results),
    "background_alpha": [0, 255], "text_font": "Noto Sans CJK TC bold italic", "max_size": [4096, 4096],
    "oversize_rejected": True, "status": "PASS"})
print("CPU tools", len(results), "PASS", sid)
