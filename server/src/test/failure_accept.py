import io
import json
import zipfile
from PIL import Image
from client import call, session, upload, tool, wait, save

sid = session("Acceptance · Failure & export")
source = upload(sid, Image.new("RGB", (80, 60), "orange"))["id"]
bad = tool(sid, "image_edit_crop", {"source": source, "width": 512, "height": 512})
child = tool(sid, "image_edit_text", {"source": bad["id"], "text": "dependent"})
batch = tool(sid, "sent_all_pending")
result, state = wait(sid, "batches", batch["id"])
assert result["status"] == "failed"
assert all(j["status"] == "failed" and j.get("error") for j in state["jobs"])
good = tool(sid, "image_edit_resize", {"source": source, "width": 160, "height": 120})
result, state = wait(sid, "batches", tool(sid, "sent_all_pending")["id"])
assert result["status"] == "done"
ident = result["images"][0]
raw = call(f"/session/{sid}/images", {"action": "export", "ids": [source, ident]}, binary=True)
with zipfile.ZipFile(io.BytesIO(raw)) as archive:
    meta = json.loads(archive.read("images.json"))
    assert len(meta) == 2 and meta[1]["parents"] == [source]
    assert Image.open(archive.open(f"image-{ident}.png")).size == (160, 120)
call(f"/session/{sid}/images", {"action": "delete", "ids": [source]})
state = call(f"/session/{sid}/state")
assert source not in [i["id"] for i in state["images"]]
assert next(i for i in state["lineage"] if i["id"] == source)["deleted"]
assert next(i for i in state["images"] if i["id"] == ident)["parents"] == [source]
save("failures", {"session": sid, "failed_job": bad["id"], "dependent_failed": child["id"],
    "recovery_image": ident, "exported_images": 2, "deleted_parent_retained_in_lineage": True, "status": "PASS"})
print("Failed jobs, dependent failure, recovery, export and deletion PASS")
