import json
import subprocess
import time
from studio_helpers import ROOT,call,record
from browser_helpers import until
from studio_recovery_helpers import restart

script=str(ROOT/'server/start.sh')
restart()
before=json.loads((ROOT/'server/data/service.json').read_text())['pid']
conflict=subprocess.run([script],capture_output=True,text=True,timeout=10)
assert conflict.returncode==1 and str(before) in conflict.stdout and 'python' in conflict.stdout,conflict.stdout
with (ROOT/'server/data/recovery-start.log').open('ab') as log:
    child=subprocess.Popen([script,'--force'],cwd=ROOT,stdout=log,
                           stderr=subprocess.STDOUT,start_new_session=True)

def replaced():
    try:
        pid=json.loads((ROOT/'server/data/service.json').read_text())['pid']
        return pid if pid!=before and call('/bootstrap')['connected'] else None
    except (OSError,ValueError):
        return None

after=until(replaced,60)
record('lifecycle',{'status':'PASS','before':before,'after':after,'conflict_report':conflict.stdout.strip(),
                    'force_replaced':True,'service_left_running':True})
print('HTTPS service restart, occupied-port PID report and --force PASS')
