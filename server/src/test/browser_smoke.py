import base64
import time
from browser_session import browser
from client import OUT, save

with browser() as driver:
    driver.set_window_rect(width=1440, height=1100)
    driver.navigate("https://127.0.0.1:8189")
    time.sleep(3)
    data = driver.execute_script('''return {title:document.title,
      notice:document.getElementById('notice').textContent,
      controls:document.querySelectorAll('button').length,
      overflow:document.documentElement.scrollWidth>window.innerWidth,
      connection:document.getElementById('connection').textContent};''')
    (OUT / "mvp-desktop.png").write_bytes(base64.b64decode(driver.screenshot()))
    save("browser-smoke", data)
    print(data)
    assert data["controls"] > 20 and not data["notice"] and not data["overflow"], data
