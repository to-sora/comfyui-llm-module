"""Apply the production metadata fix without restarting the once-read run."""
from pathlib import Path
from plugin.src.main.checkpoint_header import shapes
from plugin.src.test.api_client import request
from .studio_helpers import record


def detect():
    caps=request('/llm/capabilities')
    invalid={}
    for name in caps['checkpoints']:
        try:shapes(Path('../comfyui/models/checkpoints')/name)
        except (ValueError,KeyError,OSError) as exc:invalid[name]=str(exc)
    for key in ('checkpoints','batch_checkpoints'):
        caps[key]=[name for name in caps[key] if name not in invalid]
    record('flow-api-catalog',{'rejected':invalid,'accepted':len(caps['checkpoints']),
                             'note':'New production header validation; backend restart deferred until matrix ends.'})
    return caps
