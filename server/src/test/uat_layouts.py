from browser_helpers import click, until
from client import ROOT
from uat_common import snapshot, show


def run(driver, sid):
    driver.execute_script("document.getElementById('edit-panel').open=false;document.getElementById('chat-panel').open=false;window.scrollTo(0,0)")
    layouts = []
    for name, width, height in (("desktop",1440,1100), ("phone",480,1000), ("large",1920,1400)):
        sizes = snapshot(driver, "layout-" + name, width, height)
        assert not sizes["overflow"], sizes
        layouts.append(sizes)
    driver.set_window_rect(width=1440, height=1100)
    before = driver.execute_script("return innerWidth")
    with driver.using_context(driver.CONTEXT_CHROME):
        driver.execute_script("gBrowser.selectedBrowser.fullZoom=2.0")
    until(lambda: driver.execute_script("return innerWidth") < before)
    sizes = snapshot(driver, "layout-200-percent")
    assert not sizes["overflow"], sizes
    layouts.append(sizes)
    with driver.using_context(driver.CONTEXT_CHROME):
        driver.execute_script("gBrowser.selectedBrowser.fullZoom=1.0")
    folder = ROOT / "server/data/tmp/downloads"
    folder.mkdir(exist_ok=True)
    before_files = set(folder.glob("*.png"))
    show(driver, "download")
    click(driver, "download")
    files = until(lambda: set(folder.glob("*.png")) - before_files, timeout=30)
    assert all(p.stat().st_size > 100 for p in files)
    for path in files:
        path.unlink()
    return {"layouts": layouts, "download": True, "zoom": "200%"}
