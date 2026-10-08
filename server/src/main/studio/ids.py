import secrets
import time

ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
_last = _random = 0


def new():
    global _last, _random
    millis = max(_last, int(time.time() * 1000))
    _random = _random + 1 if millis == _last else secrets.randbits(80)
    if _random >= 1 << 80:
        millis, _random = millis + 1, 0
    _last = millis
    value = (millis << 80) | _random
    result = ""
    for _ in range(26):
        result = ALPHABET[value & 31] + result
        value >>= 5
    return result
