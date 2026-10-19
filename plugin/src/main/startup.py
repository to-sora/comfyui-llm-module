"""Reuse the established civit setup without its link-writing startup stage."""
import os
import sys
from .settings import APP,read
from .network import hosts


def command(config,cert,key,cpu=False):
    settings=read('config.yaml')
    root=(APP/settings['comfy_directory']).resolve()
    if not (root/'main.py').is_file():
        raise FileNotFoundError('The existing ComfyUI installation is unavailable')
    # These isolation/TLS flags match civit_script/start.sh. R3 prohibits running
    # its ln -sfn model-link rebuild and writing upstream runtime directories.
    cmd=[sys.executable,'-B',str(root/'main.py'),'--listen',hosts(config),
         '--port',str(config['port']),'--tls-keyfile',str(key),'--tls-certfile',str(cert),
         '--disable-all-custom-nodes','--whitelist-custom-nodes','comfyui-llm-module',
         '--disable-api-nodes','--disable-auto-launch','--disable-dynamic-vram',
         '--disable-fast-disk','--disable-mmap','--disable-pinned-memory',
         '--preview-method','latent2rgb','--user-directory',str(APP/'data/user'),
         '--input-directory',str(APP/'data/input'),'--output-directory',str(APP/'data/output'),
         '--temp-directory',str(APP/'data/tmp'),'--cache-lru',
         str(settings.get('cache_lru_entries',1))]
    if cpu:
        cmd.append('--cpu')
    from .node_path import arguments
    cmd+=arguments(root)
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
    return cmd,root,env
