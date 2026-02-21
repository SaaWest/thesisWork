import pathlib as path
import json
from collections import defaultdict, deque
#from ingestion_engine import *
import statistics
from delete_ingestion import *
#import numpy as np

class Docker_Self():
    def __init__(self):
        self.sysLogs = path.Path("system_logs/")
        #print(type(self.sysLogs))
        self.base_dirPath = list(path.Path("baseline/").glob("*.jsonl"))
        self.containers = defaultdict(self.store_container_resources)
        self.absorb = self.process()
        self.cids = [id for id in self.containers]

    def read_files(self):
        for path in self.base_dirPath:
            try:
                with open(path, 'r') as file:
                    for line in file:
                        yield json.loads(line)
            except ValueError as e:
                print(f"READ ERROR: {str(path)}: {e}")

    def store_container_resources(self):
        return {
            "cpu_percent_used": deque(),
            "disk_read": deque(), 
            "disk_write": deque(),
            "id": deque(), #container_id
            "memory_usage": deque(),
            "name": deque(),
            "network_rx_bytes": deque(),
            "network_tx_bytes": deque(),
            "pid": deque(),
            "time": deque()
                }

    def ingest(self, files):
        #cid = files.pop("id")
        cid = files.get("id")
        for key, value in files.items():
            self.containers[cid][key].append(value)

    def process(self):
        for path in self.base_dirPath:
            for sample in self.read_files():
                #print(sample)
                self.ingest(sample)

    def ratio_cpu_memoryGB(self):
        #for cpu in self.containers['cpu_percent_used']:
        for id in self.cids:
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

    def all_ratios(self):
        #data = []
        for id in self.cids: # iterate over list of cids
            cpu = self.containers[id]['cpu_percent_used']
            mem = self.containers[id]['memory_usage']
            disk_read = self.containers[id]['disk_read']
            disk_write = self.containers[id]['disk_write']        
            network_rec = self.containers[id]['network_rx_bytes']
            network_tran = self.containers[id]['network_tx_bytes']
            time = self.containers[id]['time']
            name = self.containers[id]['name']
            for c, m, dr, dw, rec, trn, t, n in zip(cpu, mem, disk_read, disk_write, network_rec, network_tran, time, name):
                yield {
                    "time": t,
                    "name": n,
                    "cpu_memGB_ratio": (float(c) / 100) / (float(m) * 0.001048576) if float(m) > 0 else 0,
                    "cpu_readWriteMB_ratio": ((float(dr) + float(dw)) / 1048576.0) / (float(c) / 100),
                    "cpu _networkMB_ratio": ((float(rec) + float(trn)) / 1048576.0) / (float(c) / 100),
                    "net_memMB_ratio": ((float(rec) + float(trn)) / 1048576.0) / (float(m) * 1.048576),
                    "disk_netMB_ratio": ((float(dr) + float(dw)) / 1048576.0) / ((float(rec) + float(trn)) / 1048576.0),
                    "disk_memMB_ratio": ((float(dr) + float(dw)) / 1048576.0) / (float(m) * 1.048576),
                }
        #return data

    def consume_data(self):
        ds = Docker_Self()
        ds.read_files()
        #ig = Ingestion_engine(self.sysLogs)
        ig = IG_engine()
        ig.read_files()
        ig.process()
        return (ds, ig)
    
    def measure_cpuMem(self):
        ds, ig = self.consume_data()
        baseline_cpuMem = {}
        ds_ratio_dict = defaultdict(list)
        ig_ratio_dict = defaultdict(list)
        anomalies = defaultdict(list)
        #for i in self.containers.items():
        for dicts in ds.ratio_cpu_memoryGB():
            name = dicts["name"]
            ratio = dicts['cpu_memGB_ratio']
            ds_ratio_dict[name].append(ratio)
            #print(ds_ratio_dict)
        for dicts in ig.ratio_cpu_memoryGB():
            #print(dicts)
            container_name = dicts['name']
            ratio = dicts['cpu_memGB_ratio']
            ig_ratio_dict[container_name].append(ratio)
            #print(ratio)
        for name, ratio in ds_ratio_dict.items():
            mean = statistics.mean(ratio)
            std_dev = statistics.stdev(ratio)
            baseline_cpuMem[name] = {'mean': mean, 'std_dev': std_dev}
        for name, ratios_ig in ig_ratio_dict.items():
            if name in baseline_cpuMem:
                mean = baseline_cpuMem[name]['mean']
                std_dev = baseline_cpuMem[name]['std_dev']
                for ratio in ratios_ig:
                    z_score = (ratio - mean) / std_dev if std_dev != 0 else 0
                    #print(z_score)
                    if abs(z_score) > 3:
                        anomalies[name].append({
                            "z_score": z_score,
                            "ratio": ratio
                        })
        # Do something better for this code below
        if anomalies:
            for container, anomaly_list in anomalies.items():
                print(f"Container: {container}")
                for anomaly in anomaly_list:
                    print(f"  Anomaly - Z-score: {anomaly['z_score']}, Ratio: {anomaly['ratio']}")



                    

        #print(type(ig))

if __name__ == "__main__":
    ds = Docker_Self()
    ds.measure_cpuMem()
    #ds.read_files()
    #print(ds.base_dirPath)
    #for cid, container in ds.containers.items():
        #print(f"Container ID: {cid}")
        #print(container)
    #for result in ds.all_ratios():
        #print(result)