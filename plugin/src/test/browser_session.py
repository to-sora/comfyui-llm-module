import contextlib
import os
from pathlib import Path
import shutil
import signal
import socket
import subprocess
import tempfile
import time
from marionette_driver.marionette import Marionette


@contextlib.contextmanager
def browser():
    root = Path(__file__).resolve().parents[3]
    profile = Path(tempfile.mkdtemp(prefix="firefox-", dir=root / "plugin/data/tmp"))
    with socket.socket(socket.AF_INET) as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    prefs = {"marionette.port": port, "network.dns.disableIPv6": True,
             "browser.shell.checkDefaultBrowser": False,
             "datareporting.policy.dataSubmissionEnabled": False}
    import json
    (profile / "user.js").write_text("\n".join(
        f"user_pref({json.dumps(k)}, {json.dumps(v)});" for k, v in prefs.items()))
    process = subprocess.Popen([str(Path.home() / "UAT-firefox/firefox/firefox"),
        "--headless", "--no-remote", "--marionette", "--profile", str(profile)],
        start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    driver = Marionette(host="127.0.0.1", port=port, socket_timeout=10)
    try:
        for _ in range(60):
            if process.poll() is not None:
                raise RuntimeError("Firefox exited before Marionette connected.")
            try:
                driver.start_session({"acceptInsecureCerts": True})
                break
            except (ConnectionError, OSError):
                time.sleep(0.5)
        else:
            raise TimeoutError("Firefox Marionette startup timed out.")
        yield driver
    finally:
        try:
            driver.delete_session()
        finally:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
            shutil.rmtree(profile, ignore_errors=True)
