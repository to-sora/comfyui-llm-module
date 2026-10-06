import base64
import time
from marionette_driver.by import By
from client import OUT, call


def click(driver, ident):
    driver.find_element(By.ID, ident).click()


def fill(driver, ident, value):
    element = driver.find_element(By.ID, ident)
    element.clear()
    element.send_keys(str(value))


def select(driver, ident, value):
    driver.execute_script('''const e=document.getElementById(arguments[0]);
      e.value=arguments[1];e.dispatchEvent(new Event('change',{bubbles:true}));''', script_args=[ident, value])


def until(check, timeout=900):
    start = time.monotonic()
    while time.monotonic() - start < timeout:
        result = check()
        if result:
            return result
        time.sleep(.4)
    raise TimeoutError("Browser action did not complete")


def idle(sid, kind, after):
    state = call(f"/session/{sid}/state")
    rows = [r for r in state[kind] if r["id"] > after]
    return state if rows and not state["busy"] else None


def screenshot(driver, name, width, height):
    driver.set_window_rect(width=width, height=height)
    driver.execute_script("window.scrollTo(0,0)")
    time.sleep(.6)
    overflow = driver.execute_script("return document.documentElement.scrollWidth>window.innerWidth")
    (OUT / (name + ".png")).write_bytes(base64.b64decode(driver.screenshot()))
    assert not overflow, f"Horizontal overflow at {width} × {height}"
    return {"width": width, "height": height, "overflow": overflow}
