import json
from pathlib import Path
import ssl
import subprocess
import sys
import time
from .api_client import request
from ..main.processes import STATE, listeners


def fixture():
    from http.server import BaseHTTPRequestHandler, HTTPServer
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"fixture":true}')
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain("plugin/data/tls/cert.pem", "plugin/data/tls/key.pem")
    server = HTTPServer(("0.0.0.0", 8188), Handler)
    server.socket = context.wrap_socket(server.socket, server_side=True)
    server.serve_forever()


def main():
    start = ["bash", "plugin/start.sh"]
    subprocess.run(start + ["--stop"], check=True)
    assert not listeners(8188), "Port has an unrelated owner; test will not replace it."
    occupied = subprocess.Popen([sys.executable, "-m", __package__ + ".lifecycle_accept", "--fixture"],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    forced = None
    try:
        for _ in range(50):
            if occupied.pid in listeners(8188):
                break
            time.sleep(0.1)
        assert occupied.pid in listeners(8188)
        refused = subprocess.run(start, capture_output=True, text=True, timeout=15)
        assert refused.returncode != 0 and str(occupied.pid) in refused.stdout
        assert "python" in refused.stdout
        forced = subprocess.Popen(start + ["--force"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(120):
            assert forced.poll() is None, "Forced startup exited."
            try:
                if "system" in request("/system_stats"):
                    break
            except (OSError, ValueError):
                pass
            time.sleep(0.5)
        else:
            raise TimeoutError("Forced server startup timed out.")
        assert occupied.poll() is not None
        worker = json.loads(STATE.read_text())["pid"]
        subprocess.run(start + ["--stop"], check=True)
        assert forced.wait(timeout=15) == 0
        assert not listeners(8188)
        proof = {"status": "PASS", "collision_report": refused.stdout.strip(),
                 "force_replaced_fixture": True, "stopped_worker": worker, "port_released": True}
        Path("fan-out/lifecycle.json").write_text(json.dumps(proof, indent=2))
        print(json.dumps(proof))
    finally:
        subprocess.run(start + ["--stop"], check=False)
        if occupied.poll() is None:
            occupied.terminate()
        occupied.wait(timeout=10)
        if forced:
            forced.wait(timeout=15)


if __name__ == "__main__":
    fixture() if "--fixture" in sys.argv else main()
