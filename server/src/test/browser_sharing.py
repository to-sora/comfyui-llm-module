import time
from marionette_driver.by import By
from browser_helpers import click, fill, select, until
from client import call


def state(sid):
    return call(f"/session/{sid}/state")


def run(driver, result):
    owner = result["session"]
    ids = [result["original"], result["edited"]]
    for ident in ids:
        driver.find_element(By.CSS_SELECTOR, f'.card[data-image-id="{ident}"] input').click()
    click(driver, "history-share")
    until(lambda: sum(i.get("shared", False) for i in state(owner)["images"]) == 2)
    fill(driver, "session-name", "Browser · Shared reader")
    click(driver, "new-session")
    reader = until(lambda: (s if (s := call('/bootstrap')['active']) != owner else None))
    time.sleep(1.5)
    shared = [i for i in state(reader)["images"] if i["operation"] == "text"]
    assert len(shared) == 1 and shared[0]["readonly"]
    alias = shared[0]["id"]
    driver.find_element(By.CSS_SELECTOR, f'.card[data-image-id="{alias}"] img').click()
    assert "read-only" in driver.find_element(By.ID, "image-size").text
    select(driver, "sessions", owner)
    until(lambda: call('/bootstrap')['active'] == owner)
    time.sleep(1.5)
    driver.find_element(By.CSS_SELECTOR, f'.card[data-image-id="{ids[1]}"] input').click()
    click(driver, "history-revoke")
    until(lambda: not next(i for i in state(owner)["images"] if i["id"] == ids[1])["shared"])
    select(driver, "sessions", reader)
    until(lambda: call('/bootstrap')['active'] == reader)
    time.sleep(1.5)
    assert alias not in [i["id"] for i in state(reader)["images"]]
    select(driver, "sessions", owner)
    until(lambda: call('/bootstrap')['active'] == owner)
    time.sleep(1.5)
    driver.find_element(By.CSS_SELECTOR, f'.card[data-image-id="{ids[1]}"] img').click()
    return {"multi_select": 2, "reader": reader, "revoked_alias": alias, "read_only": True}
