"""Keep alternate engine experiments separate from established evidence."""
import os
import re
from pathlib import Path


def output(name):
    directory = Path(__file__).resolve().parents[3]/'fan-out/studio-engine'
    group = os.environ.get('LLM_TEST_GROUP', '')
    if group:
        if not re.fullmatch(r'[A-Za-z0-9_-]+', group):
            raise ValueError('LLM_TEST_GROUP must be a directory label')
        directory /= group
    directory.mkdir(parents=True, exist_ok=True)
    return directory/name
