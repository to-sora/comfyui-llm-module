import subprocess
from studio_helpers import ROOT,call
from browser_helpers import until


def stop():
    subprocess.run([str(ROOT/'plugin/start.sh'),'--stop'],cwd=ROOT,check=True,timeout=30)
    until(lambda:not call('/bootstrap')['connected'],30)


def start():
    with (ROOT/'plugin/data/studio-start.log').open('ab') as log:
        subprocess.Popen([str(ROOT/'plugin/start.sh')],cwd=ROOT,stdout=log,
                         stderr=subprocess.STDOUT,start_new_session=True)
    until(lambda:call('/bootstrap')['connected'],120)
