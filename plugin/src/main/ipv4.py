import socket


def enable():
    if getattr(socket.getaddrinfo, "_qwen_ipv4", False):
        return
    original = socket.getaddrinfo

    def resolve(host, port, family=0, type=0, proto=0, flags=0):
        return original(host, port, socket.AF_INET, type, proto, flags)

    resolve._qwen_ipv4 = True
    socket.getaddrinfo = resolve
