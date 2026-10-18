import json
import psutil
from ..main.settings import APP
from ..main.estimate import metadata
from ..main.ram_budget import check,reserve,GB
from ..main.weight_reads import claim


def admit(source,projector,base):
    state=APP/'data/service.json'
    if state.exists():
        saved=json.loads(state.read_text())
        try:
            process=psutil.Process(saved['pid'])
            if process.create_time()==saved['created']:
                raise RuntimeError('Offline conversion is unavailable during a ComfyUI execution. '
                                   'Use an existing imported profile; do not restart to bypass R2.')
        except psutil.NoSuchProcess:
            pass
    _,size=metadata(base)
    # Full dequantized CPU weights plus the mapped GGUF and projector conversion peak.
    from pathlib import Path
    peak=Path(source).stat().st_size+Path(projector).stat().st_size*2+2*GB
    reserve(('conversion',str(source)),int(size*1.1),peak)
    claim(str(source),'GGUF text conversion')
    claim(str(projector),'GGUF projector conversion')
