import ctypes
import json
import ssl
import threading
import time
import urllib.request
from pathlib import Path


def comfy(path):
    with urllib.request.urlopen('https://127.0.0.1:8188'+path,
            context=ssl._create_unverified_context(),timeout=3) as r:
        return json.load(r)


class Observer:
    def __init__(self,pid):
        self.pid=pid
        self.host=[]
        self.models=[]
        self.phase='baseline'
        self.stop=threading.Event()
        self.low=False
        self.nvml=ctypes.CDLL('libnvidia-ml.so.1')
        self.nvml.nvmlInit_v2()
        self.device=ctypes.c_void_p()
        self.nvml.nvmlDeviceGetHandleByIndex_v2(0,ctypes.byref(self.device))
        self.threads=[threading.Thread(target=f,daemon=True) for f in (self.sample,self.status)]
        for t in self.threads:t.start()

    def sample(self):
        class Memory(ctypes.Structure):
            _fields_=[(n,ctypes.c_ulonglong) for n in ('total','free','used')]
        while not self.stop.is_set():
            memory={line.split(':')[0]:int(line.split()[1])*1024 for line in Path('/proc/meminfo').read_text().splitlines() if line.split(':')[0] in ('MemTotal','MemAvailable','SwapTotal','SwapFree')}
            free=min(memory['MemAvailable'],80_000_000_000-memory['MemTotal']+memory['MemAvailable'])
            gpu=Memory();self.nvml.nvmlDeviceGetMemoryInfo(self.device,ctypes.byref(gpu))
            rss=int(Path(f'/proc/{self.pid}/statm').read_text().split()[1])*4096
            self.host.append({'time':time.time(),'phase':self.phase,'available':memory['MemAvailable'],
                'planned_available':free,'system_used':memory['MemTotal']-memory['MemAvailable'],
                'comfy_rss':rss,'swap_used':memory['SwapTotal']-memory['SwapFree'],
                'gpu_used':gpu.used,'gpu_free':gpu.free})
            self.low=self.low or free<12*1024**3
            self.stop.wait(.5)

    def status(self):
        while not self.stop.is_set():
            try:self.models.append({'time':time.time(),'phase':self.phase,'status':comfy('/llm/status')})
            except Exception as e:self.models.append({'time':time.time(),'error':str(e)})
            self.stop.wait(2)

    def close(self):
        self.stop.set()
        for t in self.threads:t.join(5)
        self.nvml.nvmlShutdown()
        return {'host':self.host,'models':self.models}
