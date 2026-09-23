import socket


def enable():
    original = socket.getaddrinfo
    if getattr(original, "qwen_ipv4", False):
        return

    def resolve(host, port, family=0, type=0, proto=0, flags=0):
        return original(host, port, socket.AF_INET, type, proto, flags)

    resolve.qwen_ipv4 = True
    socket.getaddrinfo = resolve
