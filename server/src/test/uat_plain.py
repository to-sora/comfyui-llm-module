import time
from PIL import ImageChops, ImageStat
from marionette_driver.by import By
from browser_helpers import click, fill, until
from client import call, picture
from uat_common import state, wait_work, snapshot, save, save_image, show

PROMPT = ("Make two different pictures: a red ceramic mug on a white background, "
          "and a blue toy car on a white background. Check both pictures and tell me what you see.")


def run(driver, proof):
    driver.set_window_rect(width=1440, height=1100)
    driver.navigate("https://127.0.0.1:8189")
    until(lambda: driver.execute_script("return !!document.getElementById('chat-send')"))
    previous = call("/bootstrap")["active"]
    fill(driver, "session-name", "UAT defaults 2026-10-08")
    click(driver, "new-session")
    sid = until(lambda: (v if (v := call("/bootstrap")["active"]) != previous else None))
    proof["session"] = sid
    time.sleep(1)
    proof["defaults"] = state(sid)["session"]["settings"]
    save("defaults", proof["defaults"])
    driver.find_element(By.CSS_SELECTOR, "#chat-panel summary").click()
    fill(driver, "chat-input", PROMPT)
    show(driver, "chat-send")
    snapshot(driver, "01-plain-prompt")
    click(driver, "chat-send")
    value = wait_work(driver, sid, "chats")
    chat = value["chats"][-1]
    images = [i for i in value["images"] if not i.get("readonly")]
    proof["plain_prompt"] = {"prompt": PROMPT, "response": chat["response"],
        "tools": [m.get("name") for m in value["messages"] if m["role"] == "tool"],
        "images": [{k: i.get(k) for k in ("id", "width", "height", "settings", "sha256")} for i in images]}
    save("plain-prompt", proof["plain_prompt"])
    assert len(images) == 2, f"Expected two images, received {len(images)}"
    assert len({i["settings"]["seed"] for i in images}) == 2
    assert all(i["width"] * i["height"] >= 950000 for i in images)
    assert all(i["settings"]["cfg"] == 5.5 for i in images)
    assert all(word in chat["response"].lower() for word in ("red", "blue")), chat["response"]
    assert "sent_all_pending" in proof["plain_prompt"]["tools"]
    diff = ImageStat.Stat(ImageChops.difference(picture(sid, images[0]["id"]), picture(sid, images[1]["id"]))).mean
    assert max(diff[:3]) > 1, diff
    proof["plain_prompt"]["pixel_difference"] = diff[:3]
    for n, image in enumerate(images):
        save_image(sid, image["id"], "generated-" + str(n + 1))
    show(driver, "chat-panel")
    snapshot(driver, "02-generated-reviewed")
    proof["plain_prompt"]["status"] = "PASS"
    save("plain-prompt", proof["plain_prompt"])
    return sid
