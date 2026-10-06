import time
from pathlib import Path
from browser_session import browser
from browser_helpers import screenshot, click, until
from browser_flow import run
from browser_mask import test as mask
from client import ROOT, OUT, save, picture

started = time.monotonic()
with browser() as driver:
    driver.set_window_rect(width=1440, height=1100)
    result = run(driver)
    result["mask"] = mask(driver)
    driver.execute_script("document.getElementById('edit-panel').open=false; document.getElementById('chat-panel').open=false")
    sizes = [("desktop", 1440, 1100), ("portrait", 480, 1000), ("enlarged", 1920, 1400)]
    result["layouts"] = [screenshot(driver, "uat-" + label, w, h) for label, w, h in sizes]
    folder = ROOT / "server/data/tmp/downloads"
    folder.mkdir(exist_ok=True)
    before = set(folder.glob("*.png"))
    click(driver, "download")
    downloaded = until(lambda: set(folder.glob("*.png")) - before, timeout=30)
    assert all(p.stat().st_size > 1000 for p in downloaded)
    result["download"] = True
    for path in downloaded:
        path.unlink()
    assert not driver.execute_script("return document.getElementById('notice').textContent")
    result["elapsed_minutes"] = max(1, round((time.monotonic() - started) / 60))
    result["status"] = "PASS"
    save("browser-accept", result)
    for label in ("original", "edited"):
        picture(result["session"], result[label]).save(OUT / ("uat-" + label + ".png"))
    print(result, flush=True)
