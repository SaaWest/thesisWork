import json
from pathlib import Path
from collections import defaultdict, deque
import pandas
import os

class Ratio_Alert():
    def __init__(self, log_dir):
    #file_path = "system_logs/ab2e7b0ad971/ab2e7b0ad971_2026-02-09_19:56:21.62"
        self.system_logs = Path(log_dir)
        self.dir_paths = list(self.system_logs.glob("*/*.jsonl"))
        #self.data = pandas.DataFrame()
        self.data = []
        self.window = 1000 # for 1000 entries may need change
        self.containers = defaultdict(self.store_container_resources)

    def store_container_resources(self):
        return {"cpu_percent_used": deque(maxlen=self.window),
                "disk_read": deque(maxlen=self.window), 
                "disk_write": deque(maxlen=self.window),
                "id": deque(maxlen=self.window), #container_id
                "memory_usage": deque(maxlen=self.window),
                "name": deque(maxlen=self.window),
                "network_rx_bytes": deque(maxlen=self.window),
                "network_tx_bytes": deque(maxlen=self.window),
                "pid": deque(maxlen=self.window),
                "time": deque(maxlen=self.window)}
    
    def ingest(self, files):
        cid = files.pop("id")
        for key, value in files.items():
            self.containers[cid][key].append(value)

    def read_files(self, file_paths=None):
        if file_paths is None:
            file_paths = self.dir_paths

        for path in file_paths:
            #print(path)
            try:
                with open(path, 'r') as file:
                    for line in file:
                        yield json.loads(line)
            except ValueError as e:
                print(f"READ ERROR: {str(path)}: {e}")

    def process(self):
        for path in self.dir_paths:
            #print(path)
            for sample in self.read_files([path]):
                #print(sample)
                self.ingest(sample)
    
    def ratio_cpu_memory_time(self, cid):
        #for cpu in self.containers['cpu_percent_used']:
        cpu = self.containers[cid]['cpu_percent_used']
        mem = self.containers[cid]['memory_usage']
        time = self.containers[cid]['time']
        for t, c, m in zip(time, cpu, mem):
            yield {
                "timestamp": t,
                "cpu_memGB_ratio": float(c) / (float(m) * 0.001048576) if float(m) > 0 else 0
            }
        #return [float(c) / (float(m) *0.001048576) if float(m) > 0 else 0
                #for c, m in zip(cpu, mem)
                #]

    def ratio_cpu_diskReadWrite(self, cid):
        cpu = self.containers[cid]['cpu_percent_used']
        read = self.containers[cid]['disk_read']
        write = self.containers[cid]['disk_write']
        time = self.containers[cid]['time']
        for t, c, r, w in zip(time, cpu, read, write):
            yield {
                "time": t,
                "cpu_read/writeMB_ratio": ((float(r) + float(w)) / 1048576.0) / float(c)
            }

    def ratio_cpu_network(self, cid):
        cpu = self.containers[cid]['cpu_percent_used']
        network_rec = self.containers[cid]['network_rx_bytes']
        network_tran = self.containers[cid]['network_tx_bytes']
        time = self.containers[cid]['time']
        for t, c, rec, trn in zip (time, cpu, network_rec, network_tran):
            yield {
                "time": t,
                "cpu _networkMB": ((float(rec) + float(trn)) / 1048576.0) / float(c)
            }

    def print_data(self):
        for i in self.data:
            print(f"{i}")




if __name__ == "__main__":
    ratio = Ratio_Alert("system_logs/")
    ratio.read_files()
    #ratio.append_dir_paths()
    #print(ratio.dir_paths)
    #ratio.read_data()
    ratio.process()
    #for i in ratio.containers:
        #print(list(ratio.ratio_cpu_memory_time(i)))
    for i in ratio.containers:
        print(list(ratio.ratio_cpu_diskReadWrite(i)))
    #print(list(ratio.ratio_cpu_memory_time("940918a3399d")))
    #print(ratio.containers)
    #ratio.calculate_ratio_cpu_memory()
    #print(ratio.calculate_ratio_cpu_memory())
    #print(ratio.data)
    #ratio.print_data()

