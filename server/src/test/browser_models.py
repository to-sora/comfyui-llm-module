from marionette_driver.by import By
from browser_session import browser
from browser_helpers import click, fill, select, until, idle
from client import call, save

with browser() as driver:
    driver.set_window_rect(width=1440, height=1100)
    driver.navigate("https://127.0.0.1:8189")
    until(lambda: driver.execute_script("return !!document.getElementById('generate')"))
    old = call('/bootstrap')['active']
    fill(driver, "session-name", "Browser · Model selection")
    click(driver, "new-session")
    sid = until(lambda: (v if (v := call('/bootstrap')['active']) != old else None))
    until(lambda: driver.execute_script("return document.getElementById('model')?.value==='Qwen3.5-9B'"))
    checkpoint = "sdxl_sdXL_v10VAEFix.safetensors"
    select(driver, "checkpoint", checkpoint)
    fill(driver, "prompt", "A green ceramic bowl on a white table, studio photo")
    driver.find_element(By.CSS_SELECTOR, "#model-fields details summary").click()
    select(driver, "model", "Qwen3.5-9B-gguf")
    select(driver, "kv_quantization", "q4_0")
    fill(driver, "context_tokens", "8192")
    driver.find_element(By.CSS_SELECTOR, "#advanced summary").click()
    select(driver, "scheduler", "normal")
    fill(driver, "steps", "16")
    click(driver, "generate")
    state = until(lambda: idle(sid, "jobs", -1))
    job = state["jobs"][-1]
    assert job["status"] == "done", job
    image = next(i for i in state["images"] if i["id"] == job["image"])
    assert image["settings"]["checkpoint"] == checkpoint
    print("GUI alternate checkpoint generated",flush=True)
    until(lambda: driver.execute_script("return document.getElementById('main-image').naturalWidth>0"))
    driver.find_element(By.CSS_SELECTOR, "#chat-panel summary").click()
    fill(driver, "chat-input", "What is the bowl color? Inspect the actual image.")
    click(driver, "check-result")
    state = until(lambda: idle(sid, "chats", -1))
    chat = state["chats"][-1]
    assert chat["status"] == "done", chat
    print("GUI alternate LLM inspected",flush=True)
    actual = chat["actual_model"]
    assert actual["model"] == "Qwen3.5-9B-gguf" and actual["kv_quantization"] == "q4_0"
    assert actual["context_tokens"] == 8192
    fill(driver, "chat-input", "Change the bowl to blue. Preserve the arrangement and produce one revised image.")
    click(driver, "revise")
    revised = until(lambda: idle(sid, "chats", chat["id"]))
    assert revised["chats"][-1]["status"] == "done", revised["chats"][-1]
    children = [i for i in revised["images"] if image["id"] in i.get("parents", [])]
    assert children, "Revision must create a linked edit"
    save("browser-models", {"session": sid, "checkpoint": checkpoint, "actual_llm": actual,
         "response": chat["response"], "revision_image": children[-1]["id"], "status": "PASS"})
    print("GUI model, checkpoint, context and KV selection PASS", flush=True)
