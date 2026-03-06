import pathlib as path
from dataclasses import dataclass
import json
from collections import defaultdict, deque
from datetime import datetime
#from ingestion_engine import *
import statistics
#from delete_ingestion import * # <- change this import statement
import os # <- to get enivronment var for email
from email_alert import Email_Alert
from pathlib import Path
import time
#import numpy as np

#run using sudo -E python3 docker_self.py
class Docker_Self():
    def __init__(self):
        self.sysLogs = path.Path("system_logs/")
        #print(type(self.sysLogs))
        self.base_dirPath = list(path.Path("baseline/").glob("*.jsonl"))
        self.active_dirPath = list(path.Path("system_logs/").glob("*/*.jsonl"))
        self.self_containers = defaultdict(self.store_container_resources)
        #self.ingest_baseline_baseline = self.process_baseline()
        self.self_cids = [id for id in self.self_containers]
        self.nonSelf_containers= defaultdict(self.active_container_resources )
        self.nonSelf_cids = [id for id in self.nonSelf_containers]
        self.anomaly_dir = Path("anomaly/anomalies.txt")
        self.anomaly_dir.parent.mkdir(parents=True, exist_ok=True)
        # email from environemnt
        self.email_list = os.environ.get("test_email", " ") #do something better


    @dataclass
    #class for defaultdicts to reference mutiple values in z-score comparison
    class Anomaly:
        #id: str
        tag: str
        z_score: float
        ratio: float
        time: str            
# For establishing the self

    def read_baselineFiles(self):
        for path in self.base_dirPath:
            try:
                with open(path, 'r') as file:
                    for line in file:
                        yield json.loads(line)
            except ValueError as e:
                print(f"READ ERROR: {str(path)}: {e}")

    def ingest_baseline(self, files):
        #cid = files.pop("id")
        cid = files.get("id")
        for key, value in files.items():
            self.self_containers[cid][key].append(value)

    def process_baseline(self):
        for path in self.base_dirPath:
            for sample in self.read_baselineFiles():
                #print(sample)
                self.ingest_baseline(sample)
## above is base data process

# determining the non Self
    def read_activeFiles(self):
        #print("in read active")

        for path in self.active_dirPath:
            with open(path, "r") as f:
                f.seek(0)   # REMOVE the seek to end
                for line in f:
                    #print(line)
                    try:
                        yield json.loads(line)
                    except ValueError as e:
                        print(f"ERROR: read function {path}: {e}")
            #time.sleep(1)

    def ingest_active(self, files):
        #cid = files.pop("id")
        cid = files.get("id")
        for key, value in files.items():
            self.nonSelf_containers[cid][key].append(value)

    def process_active(self):
        #for path in self.active_dirPath:
            for sample in self.read_activeFiles():
                #print(sample)
                self.ingest_active(sample)

    def active_container_resources(self):
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

## above is for active files

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

    def self_cpu_memoryGB(self):
        for id in self.self_containers.keys():
            cpu = self.self_containers[id]['cpu_percent_used']
            mem = self.self_containers[id]['memory_usage']
            time = self.self_containers[id]['time']
            name = self.self_containers[id]['name']
            for t, c, m, n in zip(time, cpu, mem, name):
                yield {
                    "timestamp": t,
                    "name": n,
                    "cpu_memGB_ratio": (float(c) / 100) / (float(m) * 0.001048576) if float(m) > 0 else 0
                }

    def non_self_cpuMemGB(self):
        for id in self.nonSelf_containers.keys():
            cpu = self.nonSelf_containers[id]['cpu_percent_used']
            mem = self.nonSelf_containers[id]['memory_usage']
            time = self.nonSelf_containers[id]['time']
            name = self.nonSelf_containers[id]['name']
            for t, c, m, n in zip(time, cpu, mem, name):
                yield {
                    "timestamp": t,
                    "name": n,
                    "cpu_memGB_ratio": (float(c) / 100) / (float(m) * 0.001048576) if float(m) > 0 else 0
                } 

    def all_nonSelf_ratios(self):
        #data = []
        for id in self.nonSelf_containers.keys(): # iterate over list live containers
            cpu = self.nonSelf_containers[id]['cpu_percent_used']
            mem = self.nonSelf_containers[id]['memory_usage']
            disk_read = self.nonSelf_containers[id]['disk_read']
            disk_write = self.nonSelf_containers[id]['disk_write']        
            network_rec = self.nonSelf_containers[id]['network_rx_bytes']
            network_tran = self.nonSelf_containers[id]['network_tx_bytes']
            time = self.nonSelf_containers[id]['time']
            name = self.nonSelf_containers[id]['name']
            for c, m, dr, dw, rec, trn, t, n in zip(cpu, mem, disk_read, disk_write, network_rec, network_tran, time, name):
                yield {
                    "timestamp": t,
                    "name": n,
                    "cpu_memGB_ratio": (float(c) / 100) / (float(m) * 0.001048576) if float(m) > 0 else 0,
                    "cpu_readWriteMB_ratio": ((float(dr) + float(dw)) / 1048576.0) / (float(c) / 100),
                    "cpu_networkMB_ratio": ((float(rec) + float(trn)) / 1048576.0) / (float(c) / 100),
                    "net_memMB_ratio": ((float(rec) + float(trn)) / 1048576.0) / (float(m) * 1.048576),
                    "disk_netMB_ratio": ((float(dr) + float(dw)) / 1048576.0) / ((float(rec) + float(trn)) / 1048576.0),
                    "disk_memMB_ratio": ((float(dr) + float(dw)) / 1048576.0) / (float(m) * 1.048576),
                }
        #return data
    def all_Self_ratios(self):
        for id in self.self_containers.keys(): # iterate over list live containers
            cpu = self.self_containers[id]['cpu_percent_used']
            mem = self.self_containers[id]['memory_usage']
            disk_read = self.self_containers[id]['disk_read']
            disk_write = self.self_containers[id]['disk_write']        
            network_rec = self.self_containers[id]['network_rx_bytes']
            network_tran = self.self_containers[id]['network_tx_bytes']
            time = self.self_containers[id]['time']
            name = self.self_containers[id]['name']
            #disk_mb = (float(network_rec) + float(network_tran)) / 1048576.0
            for c, m, dr, dw, rec, trn, t, n in zip(cpu, mem, disk_read, disk_write, network_rec, network_tran, time, name):
                yield {
                    "timestamp": t,
                    "name": n,
                    "cpu_memGB_ratio": (float(c) / 100) / (float(m) * 0.001048576) if float(m) > 0 else 0,
                    "cpu_readWriteMB_ratio": ((float(dr) + float(dw)) / 1048576.0) / (float(c) / 100) if float(c) > 0 else 0,
                    "cpu_networkMB_ratio": ((float(rec) + float(trn)) / 1048576.0) / (float(c) / 100) if float(c) > 0 else 0,
                    "net_memMB_ratio": ((float(rec) + float(trn)) / 1048576.0) / (float(m) * 1.048576) if float(m) > 0 else 0,
                    "disk_netMB_ratio": ((float(dr) + float(dw)) / 1048576.0) / ((float(rec) + float(trn)) / 1048576.0),
                    "disk_memMB_ratio": ((float(dr) + float(dw)) / 1048576.0) / (float(m) * 1.048576) if float(m) > 0 else 0,
                }

    def exponential_moving_average(self,values, alpha=0.3):
        ema = []
        for i, v in enumerate(values):
            if i == 0:
                ema.append(v)
            else:
                ema.append(alpha * v + (1 - alpha) * ema[i-1])
        return ema
                    
    def data_init(self):
        self.process_baseline()
        self.process_active()
        return self, self
    
    # For cpu and memory ratio.
    def measure_alert(self):
        alerted_anomalies = set()

        while True:
            ds, ig = self.data_init()
            #baseline_cpuMem = {}
            ds_ratio_dict = defaultdict(list)
            ig_ratio_dict = defaultdict(list)
            anomalies = defaultdict(list)
            resource_groups = {
                "cpu_mem": ["cpu_memGB_ratio", "net_memMB_ratio"],
                "cpu_network": ["cpu_memGB_ratio", "cpu_networkMB_ratio"],
                "disk_network": ["disk_netMB_ratio", "disk_memMB_ratio"]
                }
            for dicts in ds.all_Self_ratios():
                name = dicts["name"]
                cpu_memRatio = dicts['cpu_memGB_ratio']
                cpu_RW_ratio = dicts['cpu_readWriteMB_ratio']
                cpu_NetRatio = dicts['cpu_networkMB_ratio']
                net_memRatio = dicts["net_memMB_ratio"]
                disk_netRatio = dicts['disk_netMB_ratio']
                disk_memRatio = dicts['disk_memMB_ratio']
                timestamp = dicts['timestamp']
                #ds_ratio_dict[name].append((cpu_memRatio, cpu_RW_ratio, cpu_NetRatio, net_memRatio, disk_netRatio, disk_memRatio, timestamp))
                ds_ratio_dict[(name, "cpu_memGB_ratio")].append((cpu_memRatio, timestamp))
                ds_ratio_dict[(name, "cpu_readWriteMB_ratio")].append((cpu_RW_ratio, timestamp))
                ds_ratio_dict[(name, "cpu_networkMB_ratio")].append((cpu_NetRatio, timestamp))
                ds_ratio_dict[(name, "net_memMB_ratio")].append((net_memRatio, timestamp))
                ds_ratio_dict[(name, "disk_netMB_ratio")].append((disk_netRatio, timestamp))
                ds_ratio_dict[(name, "disk_memMB_ratio")].append((disk_memRatio, timestamp))
            for dicts in ig.all_nonSelf_ratios():
                #print("in dicts 2")
                #name = dicts['name']
                #cpu_memRatio = dicts['cpu_memGB_ratio']
                #timestamp = dicts['timestamp']
                name = dicts["name"]
                cpu_memRatio = dicts['cpu_memGB_ratio']
                cpu_RW_ratio = dicts['cpu_readWriteMB_ratio']
                cpu_NetRatio = dicts['cpu_networkMB_ratio']
                net_memRatio = dicts["net_memMB_ratio"]
                disk_netRatio = dicts['disk_netMB_ratio']
                disk_memRatio = dicts['disk_memMB_ratio']
                timestamp = dicts['timestamp']
                #ig_ratio_dict[name].append((cpu_memRatio, cpu_RW_ratio, cpu_NetRatio, net_memRatio, disk_netRatio, disk_memRatio, timestamp))  
                ig_ratio_dict[(name, "cpu_memGB_ratio")].append((cpu_memRatio, timestamp))
                ig_ratio_dict[(name, "cpu_readWriteMB_ratio")].append((cpu_RW_ratio, timestamp))
                ig_ratio_dict[(name, "cpu_networkMB_ratio")].append((cpu_NetRatio, timestamp))
                ig_ratio_dict[(name, "net_memMB_ratio")].append((net_memRatio, timestamp))
                ig_ratio_dict[(name, "disk_netMB_ratio")].append((disk_netRatio, timestamp))
                ig_ratio_dict[(name, "disk_memMB_ratio")].append((disk_memRatio, timestamp))
            
            baseline = defaultdict(dict)

            for (name, metric), ratio_timestamp in ds_ratio_dict.items():

                ratios = [item[0] for item in ratio_timestamp]

                # Remove non-numeric values just in case
                ratios = [float(r) for r in ratios if isinstance(r, (int, float))]

                # Apply EMA or moving average
                ratios = self.exponential_moving_average(ratios, alpha=0.3)

                mean = statistics.mean(ratios)
                std_dev = statistics.stdev(ratios) if len(ratios) > 1 else 0

                baseline[name][metric] = {
                    "mean": mean,
                    "std_dev": std_dev
                }
            for (name, metric), ratio_entries in ig_ratio_dict.items():

                        if name not in baseline:
                            continue

                        if metric not in baseline[name]:
                            continue

                        mean = baseline[name][metric]["mean"]
                        std_dev = baseline[name][metric]["std_dev"]

                        for ratio, timestamp in ratio_entries:

                            z_score = (ratio - mean) / std_dev if std_dev != 0 else 0

                            if abs(z_score) > 5:
                                anomalies[name].append(self.Anomaly(tag=metric, z_score=z_score, ratio=ratio, time=timestamp))

            # Group anomalies by container with a time window check for 5 previous anomalies
            #grouped_threshold = defaultdict(list)
            #print("Baseline containers:", ds.self_containers.keys())
            #print("Active containers:", ig.nonSelf_containers.keys())
            #print("Grouped anomalies:", grouped_threshold)
            #print(f"goruped thresholde length {len(grouped_threshold)}")
            #anomaly_list.sort(key=lambda a: datetime.strptime(a.time, '%Y-%m-%d_%H:%M:%S.%f'))

            grouped_anomalies = defaultdict(list)

            for container, anomalies_list in anomalies.items():
                # anomalies_list contains all single-metric anomalies
                # Map them by metric for this container
                metrics_flagged = defaultdict(list)
                for a in anomalies_list:
                    metrics_flagged[a.tag].append(a)

                # Check each resource group
                for group_name, metrics in resource_groups.items():
                # Only flag group if all metrics in the group have anomalies within the same time window
                    times_to_check = []
                    for metric in metrics:
                        if metric in metrics_flagged:
                            times_to_check.append([a.time for a in metrics_flagged[metric]])

                    # Check if there’s overlap in timestamps (or within a few seconds)
                    if times_to_check and len(times_to_check) == len(metrics):
                        # naive intersection
                        common_times = set(times_to_check[0])
                        for tlist in times_to_check[1:]:
                            common_times = common_times.intersection(tlist)

                        if common_times:
                            grouped_anomalies[(container, group_name)].extend(common_times)

            for (container, group_name), common_times in grouped_anomalies.items():
                if container in alerted_anomalies:
                    continue
            
            # flatten all anomalies for this container
                containerAnomalySet = set()
                for ts in common_times:
                    for a in anomalies[container]:
                        if a.time == ts and a.tag in resource_groups[group_name]:
                            key = (a.tag, a.time, a.ratio, a.z_score)
                            containerAnomalySet.add(key)
            
                if len(containerAnomalySet) >= 5:
                    print(f"Sending alert email for container {container}")
                    anomalies_list = list(containerAnomalySet)
                    first_anomalies = anomalies_list[:5]
                    with open(self.anomaly_dir, 'a') as file:
                        file.write(container+ "\n")
                        for a in first_anomalies:   
                            file.write(f"Metric: {a[0]}, Time: {a[1]}, Ratio: {a[2]}, Z-score: {a[3]}\n")
                    alertBy_email = Email_Alert(container, self.email_list, self.anomaly_dir)
                    alertBy_email.send_alert()
                    with open(self.anomaly_dir, 'w') as file:
                        file.write("")
                        file.write("")
                    alerted_anomalies.add(container)
            time.sleep(2)

if __name__ == "__main__":
    ds = Docker_Self()
    #dock_self = Docker_Self()
    #non_self = Docker_Self()
    #dock_self.read_baselineFiles()
    #dock_self.process_baseline()
    ds.measure_alert()
