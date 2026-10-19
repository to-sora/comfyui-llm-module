"""Rollback only a new failed allocation; keep every attempted-read receipt."""
from contextlib import contextmanager
import traceback
from comfy import model_management as mm
from . import ram_budget, ram_cleanup, weight_reads


@contextmanager
def admitted(key, size, transient=0, kind='llm', discard=None):
    token = ram_budget.reserve(key, size, transient, kind)
    before = set(weight_reads.READS)
    try:
        yield
    except BaseException as exc:
        weight_reads.failed_since(before, exc)
        if token is not None:
            if discard is not None:
                discard()
            with ram_budget.LOCK:
                if ram_budget.RESERVATIONS.get(key) is token:
                    ram_budget.TRACKERS.pop(key, None)
            # Unwound loader frames may still own partially constructed tensors.
            # Preserve traceback locations while dropping those local references.
            traceback.clear_frames(exc.__traceback__)
            ram_cleanup.reclaim()
            mm.soft_empty_cache()
            ram_budget.release(key, token)
        raise
