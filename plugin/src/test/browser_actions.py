import time
import json
from marionette_driver import By

APP = "window.comfyAPI.app.app"


def open_app(browser):
    browser.set_window_rect(width=1440, height=1000)
    browser.navigate("https://127.0.0.1:8188")
    for _ in range(120):
        if browser.execute_script("return Boolean(window.comfyAPI?.app?.app?.graph)", sandbox=None):
            break
        time.sleep(0.5)
    for button in browser.find_elements(By.CSS_SELECTOR, '[role="dialog"] button[aria-label="Close"]'):
        if button.is_displayed():
            button.click()


def run_graph(browser, graph, output_node):
    result = browser.execute_async_script(
        f"const done = arguments[arguments.length-1]; {APP}.loadApiJson(window.JSON.parse(arguments[0]), 'LLM UAT')"
        ".then(()=>done('loaded')).catch(e=>done(String(e)))", [json.dumps(graph)], sandbox=None)
    assert result == "loaded", result
    browser.execute_script(f"""
        const app = {APP};
        const target = app.graph.getNodeById(arguments[0]);
        const original = target.onExecuted;
        target.__uatDone = false;
        target.onExecuted = function(output) {{
            original?.apply(this, arguments);
            this.__uatOutput = output; this.__uatDone = true;
        }};
        app.graph._nodes.forEach((node, i) => {{
            node.pos = [100 + i % 2 * 480, 140 + Math.floor(i / 2) * 480];
            node.setSize([420, Math.max(320, node.computeSize()[1])]);
        }});
        app.canvas.setDirty(true, true);
    """, [output_node], sandbox=None)
    fit(browser)
    button = next(b for b in browser.find_elements(By.XPATH, '//button[normalize-space(.)="Run"]')
                  if b.is_displayed())
    button.click()
    for _ in range(600):
        result = browser.execute_script(
            f"const n={APP}.graph.getNodeById(arguments[0]); return n.__uatDone ? n.__uatOutput : null",
            [output_node], sandbox=None)
        if result is not None:
            return result
        error = browser.execute_script(f"return {APP}.lastExecutionError || {APP}.lastNodeErrors", sandbox=None)
        if error:
            raise RuntimeError(str(error))
        time.sleep(0.5)
    raise TimeoutError("GUI execution did not complete.")


def fit(browser):
    time.sleep(0.3)
    for _ in range(50):
        blocking = browser.execute_script("return [...document.querySelectorAll('.p-blockui-mask')]"
            ".some(e=>e.getBoundingClientRect().width > 0)", sandbox=None)
        if not blocking:
            break
        time.sleep(0.2)
    for button in browser.find_elements(By.CSS_SELECTOR, 'button[aria-label^="Hide Minimap"]'):
        if button.is_displayed():
            button.click()
    buttons = browser.find_elements(By.CSS_SELECTOR, 'button[aria-label^="Fit View"]')
    if buttons:
        buttons[0].click()
    time.sleep(0.3)
