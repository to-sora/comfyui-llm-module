from marionette_driver.keys import Keys
from marionette_driver.marionette import ActionSequence
from browser_session import browser
from browser_helpers import screenshot, until
from client import save, call, OUT
import json
call("/sessions", {"id": json.loads((OUT / "browser-accept.json").read_text())["session"]})

with browser() as driver:
    driver.set_window_rect(width=1440, height=1100)
    driver.navigate("https://127.0.0.1:8189")
    until(lambda: driver.execute_script("return document.getElementById('main-image')?.naturalWidth>0"))
    driver.execute_script("document.getElementById('edit-panel').open=false;document.getElementById('chat-panel').open=false")
    rows = [screenshot(driver, "uat-" + name, w, h) for name, w, h in (
        ("desktop", 1440, 1100), ("portrait", 480, 1000), ("enlarged", 1920, 1400))]
    driver.set_window_rect(width=1440, height=1100)
    original = driver.execute_script("return window.innerWidth")
    with driver.using_context(driver.CONTEXT_CHROME):
        driver.execute_script("gBrowser.selectedBrowser.fullZoom=2.0")
    until(lambda: driver.execute_script("return window.innerWidth") < original)
    zoomed = driver.execute_script("return window.innerWidth")
    assert zoomed < original, (original, zoomed)
    rows.append(screenshot(driver, "uat-zoomed", 1440, 1100))
    save("layouts", {"viewports": rows, "zoom_inner_width": zoomed, "original_inner_width": original,
                     "status": "PASS"})
    print("Refined layouts and actual browser zoom PASS", original, zoomed)
