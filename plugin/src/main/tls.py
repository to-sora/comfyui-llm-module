import subprocess
from settings import DATA


def certificate():
    folder = DATA / "tls"
    folder.mkdir(parents=True, exist_ok=True)
    key, cert = folder / "key.pem", folder / "cert.pem"
    if not key.exists() or not cert.exists():
        subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:2048",
            "-nodes", "-days", "365", "-keyout", str(key), "-out", str(cert),
            "-subj", "/CN=ComfyUI-Qwen-Development",
            "-addext", "subjectAltName=IP:127.0.0.1,DNS:localhost"], check=True)
        key.chmod(0o600)
    return key, cert
