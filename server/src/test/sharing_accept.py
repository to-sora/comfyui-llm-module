import json
from urllib.error import HTTPError
from PIL import Image
from client import call, session, upload, picture, tool, save

owner = session("Acceptance · Owner")
ids = [upload(owner, Image.new("RGB", (64, 64), color))["id"] for color in ("red", "blue")]
reader = session("Acceptance · Reader")
assert not call(f"/session/{reader}/state")["images"]
try:
    picture(reader, ids[0])
    raise AssertionError("Cross-session access allowed")
except HTTPError as exc:
    assert exc.code == 400
call("/sessions", {"id": owner})
call(f"/session/{owner}/images", {"ids": ids, "action": "share"})
call("/sessions", {"id": reader})
shared = call(f"/session/{reader}/state")["images"]
aliases = [i["id"] for i in shared]
assert len(shared) == 2 and all(10001 <= i <= 20000 for i in aliases)
assert all(not i["parents"] and "settings" not in i for i in shared)
assert picture(reader, aliases[0]).getpixel((0, 0))[:3] == (255, 0, 0)
try:
    call(f"/session/{reader}/images", {"ids": aliases, "action": "delete"})
    raise AssertionError("Shared image deletion allowed")
except HTTPError as exc:
    assert exc.code == 400
call("/sessions", {"id": owner})
call(f"/session/{owner}/images", {"ids": [ids[0]], "action": "revoke"})
call("/sessions", {"id": reader})
assert [i["id"] for i in call(f"/session/{reader}/state")["images"]] == [aliases[1]]
try:
    picture(reader, aliases[0])
    raise AssertionError("Revoked image still accessible")
except HTTPError as exc:
    assert exc.code == 400
assert picture(reader, aliases[1]).getpixel((0, 0))[:3] == (0, 0, 255)
save("sharing", {"owner": owner, "reader": reader, "native_ids": ids,
     "aliases": aliases, "revoked": aliases[0], "remaining": aliases[1], "status": "PASS"})
print("Sharing, isolation, read-only and per-image revocation PASS")
