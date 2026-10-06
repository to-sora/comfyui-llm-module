import time
from marionette_driver.by import By
from browser_helpers import click, fill, select, until, idle
from client import call


def run(driver):
    driver.navigate("https://127.0.0.1:8189")
    until(lambda: driver.execute_script("return !!document.getElementById('generate')"))
    old = call("/bootstrap")["active"]
    fill(driver, "session-name", "Studio · Browser acceptance")
    click(driver, "new-session")
    sid = until(lambda: (v if (v := call("/bootstrap")["active"]) != old else None))
    time.sleep(1.5)
    fill(driver, "prompt", "A single red ceramic mug centered on a seamless pure white background, studio product photograph, soft shadow, high detail")
    driver.find_element(By.CSS_SELECTOR, "#advanced summary").click()
    fill(driver, "seed", "24680")
    select(driver, "scheduler", "normal")
    driver.find_element(By.CSS_SELECTOR, "#model-fields details summary").click()
    select(driver, "kv_quantization", "hqq_8")
    click(driver, "generate")
    state = until(lambda: idle(sid, "jobs", -1))
    assert state["jobs"][-1]["status"] == "done", state["jobs"][-1]
    original = state["jobs"][-1]["image"]
    print("GUI generated", sid, original, flush=True)
    assert state["images"][0]["settings"]["seed"] == 24680
    driver.refresh()
    until(lambda: driver.execute_script("return document.getElementById('main-image')?.naturalWidth>0"))
    driver.find_element(By.CSS_SELECTOR, "#chat-panel summary").click()
    fill(driver, "chat-input", "Is there a red mug? Describe the background color and any visible defects.")
    click(driver, "check-result")
    state = until(lambda: idle(sid, "chats", -1))
    assert state["chats"][-1]["status"] == "done", state["chats"][-1]
    print("GUI inspected", flush=True)
    click(driver, "edit-selected")
    select(driver, "edit-operation", "text")
    fill(driver, "edit-text", "RED / 紅")
    fill(driver, "edit-color", "#102030")
    select(driver, "edit-font", "Noto Sans CJK TC")
    click(driver, "edit-bold")
    click(driver, "edit-italic")
    last = state["jobs"][-1]["id"]
    click(driver, "apply-edit")
    print("GUI edit submitted", flush=True)
    state = until(lambda: idle(sid, "jobs", last))
    assert state["jobs"][-1]["status"] == "done", state["jobs"][-1]
    edited = state["jobs"][-1]["image"]
    assert next(i for i in state["images"] if i["id"] == edited)["parents"] == [original]
    time.sleep(1)
    click(driver, "compare")
    assert driver.execute_script("return getComputedStyle(document.getElementById('before-image')).display") == "block"
    click(driver, "compare")
    return {"session": sid, "original": original, "edited": edited,
            "response": state["chats"][-1]["response"], "refresh_recovered": True}
