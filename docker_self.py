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
                    print(line)
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

    #def self_cpu_memoryGB(self):
        #for cpu in self.containers['cpu_percent_used']:
        #for id in self.self_cids:
            #cpu = self.self_containers[id]['cpu_percent_used']
            #mem = self.self_containers[id]['memory_usage']
            #time = self.self_containers[id]['time']
            #name = self.self_containers[id]['name']
            #for t, c, m, n in zip(time, cpu, mem, name):
                #yield {
                    #"timestamp": t,
                    #"name": n,
                    #"cpu": c,
                    #"cpu_memGB_ratio": (float(c) / 100) / (float(m) * 0.001048576) if float(m) > 0 else 0
                #}

    #def non_self_cpuMemGB(self):
        #for cpu in self.containers['cpu_percent_used']:
        #for id in self.nonSelf_cids:
            #cpu = self.nonSelf_containers[id]['cpu_percent_used']
            #mem = self.nonSelf_containers[id]['memory_usage']
            #time = self.nonSelf_containers[id]['time']
            #name = self.nonSelf_containers[id]['name']
            #for t, c, m, n in zip(time, cpu, mem, name):
                #yield {
                    #"timestamp": t,
                    #"name": n,
                    #"cpu": c,
                    #"cpu_memGB_ratio": (float(c) / 100) / (float(m) * 0.001048576) if float(m) > 0 else 0
                #}
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

    def all_ratios(self):
        #data = []
        for id in self.nonSelf_cids: # iterate over list of cids
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

    def data_init(self):
        self.process_baseline()
        self.process_active()
        return self, self
    
    # For cpu and memory ratio.
    def measure_alert(self):
        print("In Measure alert")
        while True:
            ds, ig = self.data_init()
            baseline_cpuMem = {}
            ds_ratio_dict = defaultdict(list)
            ig_ratio_dict = defaultdict(list)
            anomalies = defaultdict(list)
            # Collect ratio data from ds
            print("before first for loop")
            for dicts in ds.self_cpu_memoryGB():
                print("in dicts 1")
                name = dicts["name"]
                ratio = dicts['cpu_memGB_ratio']
                timestamp = dicts['timestamp']
                ds_ratio_dict[name].append((ratio, timestamp))
            # Collect ratio data from ig
            print("before second for loop")
            for dicts in ig.non_self_cpuMemGB():
                print("in dicts 2")
                container_name = dicts['name']
                ratio = dicts['cpu_memGB_ratio']
                timestamp = dicts['timestamp'] 
                ig_ratio_dict[container_name].append((ratio, timestamp))  
            # Calculate mean and std_dev for each container from ds data
            print("before third for loop")
            for name, ratio_and_timestamp in ds_ratio_dict.items():
                print("in ds ratio")
                ratios = [item[0] for item in ratio_and_timestamp]
                mean = statistics.mean(ratios)
                std_dev = statistics.stdev(ratios)
                baseline_cpuMem[name] = {'mean': mean, 'std_dev': std_dev}
            # Check for anomalies in ig data based on baseline_cpuMem
            print("before fourth for loop")
            for name, ratios_and_timestamps in ig_ratio_dict.items():
                print("in ig ratio.items")
                if name in baseline_cpuMem:
                    mean = baseline_cpuMem[name]['mean']
                    std_dev = baseline_cpuMem[name]['std_dev']
                    for ratio, timestamp in ratios_and_timestamps:
                        print("in ratio timestamp")
                        # Calculate z-score
                        z_score = (ratio - mean) / std_dev if std_dev != 0 else 0
                    
                        # If z-score is greater than 3 or less than -3, mark it as an anomaly
                        if abs(z_score) > 3:
                            anomalies[name].append(self.Anomaly(z_score=z_score, ratio=ratio, time=timestamp))

            # Group anomalies by container with a time window check for 5 previous anomalies
            grouped_threshold = defaultdict(list)
            #print("Baseline containers:", ds.self_containers.keys())
            #print("Active containers:", ig.nonSelf_containers.keys())
            #print("Grouped anomalies:", grouped_threshold)
            #print(f"goruped thresholde length {len(grouped_threshold)}")
            #anomaly_list.sort(key=lambda a: datetime.strptime(a.time, '%Y-%m-%d_%H:%M:%S.%f'))

            for container, anomaly_list in anomalies.items():

                # Sort anomalies chronologically
                anomaly_list.sort(key=lambda a: datetime.strptime(a.time, '%Y-%m-%d_%H:%M:%S.%f'))

                # Iterate through each anomaly and check the previous 5 neighbors
                i = 5
                while i < len(anomaly_list):

                    time_deltas = []
                    current_time = datetime.strptime(anomaly_list[i].time, '%Y-%m-%d_%H:%M:%S.%f')

                    for j in range(1, 6):
                        prev_index = i - j
                        if prev_index < 0:
                            break

                        prev_time = datetime.strptime(anomaly_list[prev_index].time,'%Y-%m-%d_%H:%M:%S.%f')

                        time_diff = (current_time - prev_time).total_seconds()
                        time_deltas.append(time_diff)

                    if len(time_deltas) == 5 and all(t < 5 for t in time_deltas):
                        grouped_threshold[container].append(anomaly_list[i-5:i+1])
                        i += 6
                    else:
                        i += 1
            printed_anomalies = set()
            print(f"anomalies set in measure alert {len(printed_anomalies)}")
            containerID_email = "" 
            containerID_anomalies = ""
            #containerID_anomalies = ""
            for container, group in grouped_threshold.items():
                #print(f"\nAttack on Docker image: {container[1:]}")
                containerID_email = container[1:] + "\n"
                for anomaly_group in group:
                    #print(f"CPU and memory resource Anomaly:")
                    for anomaly in anomaly_group:
                        key = (anomaly.time, anomaly.ratio, anomaly.z_score)
                        if key not in printed_anomalies:
                            printed_anomalies.add(key)
                            #print(f"Anomaly - Z-score: {anomaly.z_score}, "
                            #f"Ratio: {anomaly.ratio}, "
                            #f"Time: {anomaly.time}")
                            containerID_anomalies += (f"Anomaly - Z-score: {anomaly.z_score},"
                            + f"Ratio: {anomaly.ratio}, "
                            + f"Time: {anomaly.time}\n")
                with open(self.anomaly_dir, 'a') as file:
                    file.write(containerID_email)
                    file.write(containerID_anomalies)
                #grouped_threshold["test_container"] = [["fake_anomaly"]]
                alertBy_email = Email_Alert(container[1:], self.email_list, self.anomaly_dir) # <- DO NOT DELETE#DO NOT DELETE
                alertBy_email.send_alert() # <-DO NOT DELETE
                containerID_anomalies = ""
                containerID_email = ""
                del alertBy_email
            time.sleep(2)
        #if grouped_threshold:
            #for container, group in grouped_threshold.items():
                #print(f"Attack on Docker image: {container[1:]}")
                #alertBy_email = Email_Alert(container[1:], self.email_list) # <- DO NOT DELETE#DO NOT DELETE
                #alertBy_email.send_alert() # <-DO NOT DELETE
                #for anomaly_group in group:
                    #print(f"CPU and memory resource Anomaly:")
                    #for anomaly in anomaly_group:
                        #print(f"Anomaly - Z-score: {anomaly.z_score}, Ratio: {anomaly.ratio}, Time: {anomaly.time}")
        #del alertBy_email # DO NOT DELETE
if __name__ == "__main__":
    ds = Docker_Self()
    #dock_self = Docker_Self()
    #non_self = Docker_Self()
    #dock_self.read_baselineFiles()
    #dock_self.process_baseline()
    ds.measure_alert()
    #while True:
        #ig = Ingestion_engine(self.sysLogs)
        #ig = IG_engine()
        #non_self.read_activeFiles()
        #non_self.process_active()
        #non_self.measure_alert(dock_self, non_self)
    #ds.read_files()
    #print(ds.base_dirPath)
    #for cid, container in ds.containers.items():
        #print(f"Container ID: {cid}")
        #print(container)
    #for result in ds.all_ratios():
        #print(result)