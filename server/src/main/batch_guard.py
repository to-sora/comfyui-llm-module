from .errors import UserError
from .records import flat
from .settings import read


def check(e, sid, inline):
    if e.active and e.active["kind"] == "chat":
        if not inline:
            raise UserError("The assistant is managing this batch. Stop it before manual submission.")
        count = sum(b["id"] > e.active["id"] for b in flat(e.db, sid, "batch"))
        if count >= 1 + read().get("max_revision_batches", 2):
            raise UserError("Revision batch limit reached. Pending jobs remain available for manual review.")
