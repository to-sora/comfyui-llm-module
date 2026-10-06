from client import call, session, tool, wait, save

sid = session("Acceptance · Image lineage")
call(f"/session/{sid}/settings", {"width": 512, "height": 512, "steps": 12, "scheduler": "normal"})
generated = tool(sid, "image_gen_sdxl_text", {"prompt": "An orange fruit on a white background", "seed": 384})
text = tool(sid, "image_edit_text", {"source": generated["id"], "text": "ORANGE", "size": 40, "color": "#001122"})
removed = tool(sid, "image_edit_remove_background", {"source": text["id"]})
batch = tool(sid, "sent_all_pending")
result, state = wait(sid, "batches", batch["id"])
assert result["status"] == "done", result
produced = result["produced_images"]
assert len(produced) == 3 and result["images"] == [produced[-1]]
images = {i["id"]: i for i in state["images"]}
assert images[produced[0]]["parents"] == []
assert images[produced[1]]["parents"] == [produced[0]]
assert images[produced[2]]["parents"] == [produced[1]]
call(f"/session/{sid}/images", {"action": "share", "ids": [produced[-1]]})
state = call(f"/session/{sid}/state")
assert next(i for i in state["images"] if i["id"] == produced[-1])["shared"]
assert any(e["image"] == produced[-1] and e["action"] == "shared" for e in state["events"])
save("lineage", {"session": sid, "jobs": [generated["id"], text["id"], removed["id"]],
    "images": produced, "operations": [images[i]["operation"] for i in produced],
    "final_only_review": result["images"], "share_event": True, "status": "PASS"})
print("Single batch: SDXL → text → background removal → shared final PASS")
