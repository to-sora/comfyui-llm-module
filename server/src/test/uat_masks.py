from PIL import Image
import numpy as np
from marionette_driver.by import By
from marionette_driver.marionette import ActionSequence
from browser_helpers import click, fill, select, until
from client import ROOT, picture
from uat_common import state, wait_work, show, save_image, snapshot
from uat_edits import choose


def upload(driver, sid, size):
    before = {i["id"] for i in state(sid)["images"]}
    path = ROOT / "server/data/tmp/uat-upload.png"
    Image.new("RGB", size, "steelblue").save(path)
    try:
        driver.find_element(By.ID, "file-input").send_keys(str(path))
        item = until(lambda: next((i for i in state(sid)["images"] if i["id"] not in before), None))
        choose(driver, item["id"])
        return item
    finally:
        path.unlink(missing_ok=True)


def run(driver, sid):
    big = upload(driver, sid, (8000, 6000))
    assert (big["width"], big["height"]) == (4096, 3072)
    odd = upload(driver, sid, (321, 241))
    select(driver, "mode", "inpaint")
    click(driver, "mask-enabled")
    show(driver, "viewport")
    x, y = driver.execute_script("const r=document.getElementById('mask-canvas').getBoundingClientRect();return [Math.round(r.x+r.width/2),Math.round(r.y+r.height/2)]")
    ActionSequence(driver, "pointer", "mask", {"pointerType": "mouse"}).pointer_move(x-35,y).pointer_down().pointer_move(x+35,y,200).pointer_up().perform()
    fill(driver, "prompt", "A red dot on a blue background")
    previous = state(sid)["jobs"][-1]["id"]
    show(driver, "generate")
    click(driver, "generate")
    value = wait_work(driver, sid, "jobs", previous)
    image_id = value["jobs"][-1]["image"]
    mask = next(i for i in reversed(value["images"]) if i["operation"] == "mask")
    before, after = np.array(picture(sid, odd["id"])), np.array(picture(sid, image_id))
    painted = np.array(picture(sid, mask["id"]).convert("L")) > 0
    assert before.shape == after.shape == (241, 321, 4)
    assert np.array_equal(before[~painted], after[~painted])
    changed = int(np.any(before[painted] != after[painted], axis=1).sum())
    assert changed > 0
    choose(driver, image_id)
    show(driver, "viewport")
    snapshot(driver, "04-odd-size-inpaint")
    save_image(sid, image_id, "inpainted")
    return {"phone_upload": [4096, 3072], "source": odd["id"], "image": image_id,
            "size": [321, 241], "unchanged_outside_mask": True, "changed_pixels": changed}
