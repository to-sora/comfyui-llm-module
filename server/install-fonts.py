import socket
import urllib.request
from pathlib import Path

resolve=socket.getaddrinfo
socket.getaddrinfo=lambda host,port,family=0,type=0,proto=0,flags=0:resolve(host,port,socket.AF_INET,type,proto,flags)
folder=Path(__file__).resolve().parent/'web-studio/fonts'
folder.mkdir(parents=True,exist_ok=True)
sources={
    'geist.woff2':'https://fonts.gstatic.com/s/geist/v5/gyByhwUxId8gMEwcGFU.woff2',
    'geist-mono.woff2':'https://fonts.gstatic.com/s/geistmono/v6/or3nQ6H-1_WfwkMZI_qYFrcdmg.woff2',
    'OFL.txt':'https://raw.githubusercontent.com/google/fonts/main/ofl/geist/OFL.txt'}
for name,url in sources.items():
    path=folder/name
    if not path.is_file():
        with urllib.request.urlopen(url,timeout=30) as response:
            path.write_bytes(response.read())

# Keep a project-local CJK font for text overlays.
import shutil
image_fonts=Path(__file__).resolve().parent/'data/fonts'
image_fonts.mkdir(parents=True,exist_ok=True)
source=Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
if source.is_file() and not (image_fonts/source.name).exists():
    shutil.copyfile(source,image_fonts/source.name)
