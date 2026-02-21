import json
from pathlib import Path
from collections import defaultdict, deque
import pandas
import os

class Ingestion_engine():
    def __init__(self, log_dir):
    #file_path = "system_logs/ab2e7b0ad971/ab2e7b0ad971_2026-02-09_19:56:21.62"
        self.system_logs = Path(log_dir)
        self.dir_paths = list(self.system_logs.glob("*/*.jsonl"))
        #self.data = pandas.DataFrame()
        self.data = [] #remove
        self.window = 1000 # for 1000 entries may need change
        self.containers = defaultdict(self.store_container_resources)
        self.cids = [id for id in self.containers]
        print(self.cids)

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
            #print(type(file_paths))
        for path in file_paths:
            #print(type(file_paths))
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

    def ratio_cpu_memoryGB(self):
        #for cpu in self.containers['cpu_percent_used']:
        for id in self.cids:
            print(id)
            cpu = self.containers[id]['cpu_percent_used']
            mem = self.containers[id]['memory_usage']
            time = self.containers[id]['time']
            name = self.containers[id]['name']
            for t, c, m, n in zip(time, cpu, mem, name):
                yield {
                    "timestamp": t,
                    "name": n,
                    #"cpu": c,
                    "cpu_memGB_ratio": (float(c) / 100) / (float(m) * 0.001048576) if float(m) > 0 else 0
                } 
    #def ratio_cpu_memoryGB(self, cid):
        #for cpu in self.containers['cpu_percent_used']:
        #cpu = self.containers[cid]['cpu_percent_used']
        #mem = self.containers[cid]['memory_usage']
        #time = self.containers[cid]['time']
        #name = self.containers[cid]['name']
        #for t, c, m, n in zip(time, cpu, mem, name):
            #yield {
                #"timestamp": t,
                #"name": n,
                #"cpu": c,
                #"cpu_memGB_ratio": (float(c) / 100) / (float(m) * 0.001048576) if float(m) > 0 else 0
            #}
        #return [float(c) / (float(m) *0.001048576) if float(m) > 0 else 0
                #for c, m in zip(cpu, mem)
                #]

    def ratio_cpu_diskReadWriteMB(self, cid):
        cpu = self.containers[cid]['cpu_percent_used']
        read = self.containers[cid]['disk_read']
        write = self.containers[cid]['disk_write']
        time = self.containers[cid]['time']
        name = self.containers[cid]['name']
        for t, c, r, w, n in zip(time, cpu, read, write, name):
            yield {
                "time": t,
                "name": n,
                "cpu_readWriteMB": ((float(r) + float(w)) / 1048576.0) / (float(c) / 100)
            }

    def ratio_cpu_networkMB(self, cid):
        cpu = self.containers[cid]['cpu_percent_used']
        network_rec = self.containers[cid]['network_rx_bytes']
        network_tran = self.containers[cid]['network_tx_bytes']
        time = self.containers[cid]['time']
        name = self.containers[cid]['name']
        for t, c, rec, trn, n in zip(time, cpu, network_rec, network_tran, name):
            yield {
                "time": t,
                "name": n,
                "cpu _networkMB": ((float(rec) + float(trn)) / 1048576.0) / float(c)
            }
    
    def ratio_mem_diskMB(self, cid):
        mem = self.containers[cid]['memory_usage']
        read = self.containers[cid]['disk_read']
        write = self.containers[cid]['disk_write']
        time = self.containers[cid]['time']
        name = self.containers[cid]['name']
        for m, r, w, t, n in zip(mem, read, write, time, name):
            yield {
                "time": t,
                "name": n,
                "disk_memMB": ((float(r) + float(w)) / 1048576.0) / (float(m) * 1.048576)
            }

    def ratio_mem_netMB(self, cid):
        mem = self.containers[cid]['memory_usage']
        network_rec = self.containers[cid]['network_rx_bytes']
        network_tran = self.containers[cid]['network_tx_bytes']
        time = self.containers[cid]['time']
        name = self.containers[cid]['name']
        for m, rec, trn, t, n in zip(mem, network_rec, network_tran, time, name):
            yield {
               "time": t,
               "name": n,
               "net_memMB": ((float(rec) + float(trn)) / 1048576.0) / (float(m) * 1.048576)
            }
    def ratio_disk_netMB(self, cid):
        disk_read = self.containers[cid]['disk_read']
        disk_write = self.containers[cid]['disk_write']        
        network_rec = self.containers[cid]['network_rx_bytes']
        network_tran = self.containers[cid]['network_tx_bytes']
        time = self.containers[cid]['time']
        name = self.containers[cid]['name']
        for dr, dw, rec, trn, t, n in zip(disk_read, disk_write, network_rec, network_tran, time, name):
            yield {
                "time": t,
                "name": n,
                "disk_netMB": ((float(dr) + float(dw)) / 1048576.0) / ((float(rec) + float(trn)) / 1048576.0)
            }

    def all_ratios(self, cid):
        cpu = self.containers[cid]['cpu_percent_used']
        mem = self.containers[cid]['memory_usage']
        disk_read = self.containers[cid]['disk_read']
        disk_write = self.containers[cid]['disk_write']        
        network_rec = self.containers[cid]['network_rx_bytes']
        network_tran = self.containers[cid]['network_tx_bytes']
        time = self.containers[cid]['time']
        name = self.containers[cid]['name']
        for c, m, dr, dw, rec, trn, t, n in zip(cpu, mem, disk_read, disk_write, network_rec, network_tran, time, name):
            yield {
                "time": t,
                "name": n,
                "cpu_memGB_ratio": (float(c) / 100) / (float(m) * 0.001048576) if float(m) > 0 else 0,
                "cpu_readWriteMB_ratio": ((float(dr) + float(dw)) / 1048576.0) / (float(c) / 100),
                "cpu _networkMB": ((float(rec) + float(trn)) / 1048576.0) / (float(c) / 100),
                "net_memMB": ((float(rec) + float(trn)) / 1048576.0) / (float(m) * 1.048576),
                "disk_netMB": ((float(dr) + float(dw)) / 1048576.0) / ((float(rec) + float(trn)) / 1048576.0),
                "disk_memMB": ((float(dr) + float(dw)) / 1048576.0) / (float(m) * 1.048576),
            }


    def print_data(self):
        for i in self.data:
            print(f"{i}")




if __name__ == "__main__":
    ratio = Ingestion_engine("system_logs/")
    ratio.read_files()
    #ratio.append_dir_paths()
    #print(ratio.dir_paths)
    #ratio.read_data()
    ratio.process()
    for i in ratio.containers:
        print(list(ratio.ratio_cpu_memoryGB(i)))
    #for i in ratio.containers:
        #print(list(ratio.ratio_cpu_diskReadWrite(i)))
    #print(list(ratio.ratio_cpu_memory_time("940918a3399d")))
    #print(ratio.containers)
    #ratio.calculate_ratio_cpu_memory()
    #print(ratio.calculate_ratio_cpu_memory())
    #print(ratio.data)
    #ratio.print_data()

