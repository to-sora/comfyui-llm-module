import ipaddress
import socket


def addresses(config):
    policy = config["policy"]
    if policy == "public":
        return ["0.0.0.0"]
    if policy == "local":
        return ["127.0.0.1"]
    if policy != "standard":
        raise ValueError("policy must be local, standard, or public")
    import psutil
    result = [a.address for name, entries in psutil.net_if_addrs().items()
              if name.startswith(("wg", "tails")) for a in entries
              if a.family == socket.AF_INET]
    if not result:
        raise RuntimeError("standard policy requires a wg* or tails* IPv4 address")
    return result


def whitelist(config):
    return {str(ipaddress.IPv4Address(v.strip()))
            for v in config["whitelist"].split(",") if v.strip()}
