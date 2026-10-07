import time
from marionette_driver.by import By
from browser_helpers import click, fill, select, until
from browser_mask import test as brush
from client import picture
from uat_common import state, wait_work, show, save_image, snapshot


def choose(driver, ident):
    until(lambda: driver.find_elements(By.CSS_SELECTOR, f'.card[data-image-id="{ident}"] img'))
    driver.find_element(By.CSS_SELECTOR, f'.card[data-image-id="{ident}"] img').click()
    until(lambda: driver.execute_script("return document.getElementById('image-title').textContent.includes(arguments[0])",
                                        script_args=[f"#{ident} ·"]))
    until(lambda: driver.execute_script("return document.getElementById('main-image').complete"))


def text_edit(driver, sid):
    value = state(sid)
    original = next(i for i in value["images"] if not i.get("readonly") and i["operation"] == "sdxl_text")
    source = picture(sid, original["id"]).tobytes()
    choose(driver, original["id"])
    show(driver, "edit-selected")
    click(driver, "edit-selected")
    select(driver, "edit-operation", "text")
    fill(driver, "edit-text", "UAT 08 OCT")
    fill(driver, "edit-color", "#102030")
    previous = value["jobs"][-1]["id"]
    show(driver, "apply-edit")
    click(driver, "apply-edit")
    value = wait_work(driver, sid, "jobs", previous)
    edited = next(i for i in value["images"] if i["id"] == value["jobs"][-1]["image"])
    assert edited["parents"] == [original["id"]]
    assert picture(sid, original["id"]).tobytes() == source
    assert picture(sid, edited["id"]).tobytes() != source
    choose(driver, edited["id"])
    driver.execute_script("document.getElementById('edit-panel').open=false")
    show(driver, "compare")
    click(driver, "compare")
    assert driver.execute_script("return getComputedStyle(document.getElementById('before-image')).display") == "block"
    snapshot(driver, "03-text-edit-compare")
    click(driver, "compare")
    saved = brush(driver)
    save_image(sid, original["id"], "original")
    save_image(sid, edited["id"], "text-edited")
    driver.refresh()
    until(lambda: driver.execute_script("return document.getElementById('main-image')?.naturalWidth>0"))
    return {"source": original["id"], "edited": edited["id"], "source_unchanged": True,
            "compare": True, "brush": saved, "refresh_recovered": True}
