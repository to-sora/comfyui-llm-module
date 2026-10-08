import time


def until(check, timeout=900):
    start = time.monotonic()
    while time.monotonic() - start < timeout:
        result = check()
        if result:
            return result
        time.sleep(.4)
    raise TimeoutError("Browser action did not complete")
