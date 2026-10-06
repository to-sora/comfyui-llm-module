from client import call, session, tool, wait, save, picture

sid = session("Acceptance · SDXL")
call(f"/session/{sid}/settings", {"width": 512, "height": 512, "steps": 12})
jobs = [tool(sid, "image_gen_sdxl_text", {"prompt": prompt, "seed": seed}) for seed, prompt in (
    (431, "A bright red toy car on a pure white background, studio product photo, no text"),
    (432, "A blue ceramic mug on a pure white background, studio product photo, no text"))]
assert all(j["status"] == "pending" for j in jobs), jobs
batch = tool(sid, "sent_all_pending")
result, state = wait(sid, "batches", batch["id"])
assert result["status"] == "done", result
assert len(result["images"]) == 2
for ident in result["images"]:
    image = picture(sid, ident)
    assert image.size == (512, 512)
    image.save(__import__('client').OUT / f"smoke-{ident}.png")
save("smoke", {"session": sid, "jobs": [j["id"] for j in jobs],
               "batch": result["id"], "images": result["images"], "status": result["status"]})
print("SDXL batch", sid, result["images"], flush=True)
