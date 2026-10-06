import json
import time
from PIL import Image
from marionette_driver.by import By
from browser_session import browser
from browser_helpers import until, click, screenshot
from browser_sharing import run
from client import call, OUT, ROOT, save

result = json.loads((OUT / "browser-accept.json").read_text())
with browser() as driver:
    driver.set_window_rect(width=1440, height=1100)
    driver.navigate("https://127.0.0.1:8189")
    until(lambda: driver.execute_script("return document.querySelectorAll('.card').length>0"))
    sharing = run(driver, result)
    sid = result["session"]
    before = {i["id"] for i in call(f"/session/{sid}/state")["images"]}
    source = ROOT / "server/data/tmp/browser-upload.png"
    Image.new("RGB", (320, 240), "seagreen").save(source)
    driver.find_element(By.ID, "file-input").send_keys(str(source))
    def uploaded():
        state = call(f"/session/{sid}/state")
        return [i for i in state["images"] if i["id"] not in before]
    images = until(uploaded)
    assert images[0]["width"] == 320 and images[0]["height"] == 240
    source.unlink()
    time.sleep(1)
    driver.find_element(By.CSS_SELECTOR, f'.card[data-image-id="{result["edited"]}"] input').click()
    click(driver, "history-final")
    until(lambda: next(i for i in call(f"/session/{sid}/state")["images"] if i["id"] == result["edited"]).get("final"))
    driver.find_element(By.CSS_SELECTOR, f'.card[data-image-id="{result["edited"]}"] img').click()
    driver.execute_script("document.querySelector('#lineage').closest('details').open=true")
    screenshot(driver, "uat-lineage", 1440, 1100)
    save("browser-extra", {"sharing": sharing, "upload_size": [320, 240], "marked_final": result["edited"], "status": "PASS"})
    print("GUI multi-selection, sharing, revocation, upload and final marker PASS")
