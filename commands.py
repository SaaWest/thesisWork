import os
import subprocess
import json
import time
from datetime import datetime, timezone
import pathlib
import multiprocessing
from multiprocessing import Manager
import psutil

#pid = os.getpid()
#python_process = psutil.Process(pid)

def find_containerID():
  
  #result = subprocess.check_output("docker ps -a | awk 'NR > 1 {print $1}'", shell=True).decode().strip()
  result = subprocess.check_output("docker ps -q", shell=True).decode().strip()
  ids = [i for i in result.split('\n')]
  #print(ids)
  return ids

def create_folders(ids):
  ids = find_containerID()
  for id in ids:
    #if not os.path.exists("system_logs/{id}"):
    os.makedirs(f"system_logs/{id}", exist_ok=True)

def resource_query(container_ids):
  
  #container_ids = find_containerID()
  #create_folders(container_ids)
  
    query = f"SELECT process.id, process.name, SUM(process.cpu) AS cpu_percent, "\
      + f"SUM(process.mem) AS mem_percent, SUM(p.disk_bytes_read) AS disk_read, " \
      + f"SUM(p.disk_bytes_written) AS disk_write "\
      + f"FROM docker_container_processes AS process "\
      + f"JOIN processes AS p ON p.pid = process.pid "\
      + f"WHERE process.id = '{container_ids}' "\
      + f"GROUP BY process.id;"

    #query = f"SELECT basic.pid, stats.id, stats.name, stats.network_rx_bytes, stats.network_tx_bytes, " \
      #+ f"stats.memory_usage, stats.disk_read, stats.disk_write, (((stats.cpu_total_usage - stats.pre_cpu_total_usage)*1.0 / " \
      #+ f"(stats.system_cpu_usage - stats.pre_system_cpu_usage)*1.0) * online_cpus)*100 AS cpu_percent_used " \
      #+ f"FROM docker_container_stats AS stats JOIN " \
      #+ f"docker_containers AS basic ON stats.id = basic.id WHERE basic.id='{container_ids}'"
    result = subprocess.run(["osqueryi", '--json', query], check=True, capture_output=True, text=True)
    results = json.loads(result.stdout)
    #print(results[0])
    #print("\n")
    return results[0]

def network_query(container_id):
  #for cid in container_id:
    #rc_bytes = subprocess.run(f"docker exec {cid} cat /proc/net/dev", shell=True, capture_output= True, text=True)
    #print()
    #for line in rc_bytes.stdout.strip():
      #print(line)
  try:
    net_rx = f"docker exec {container_id} cat /sys/class/net/eth0/statistics/rx_bytes"
    rx = int(subprocess.check_output(net_rx, shell=True))
    net_tx = f"docker exec {container_id} cat /sys/class/net/eth0/statistics/tx_bytes"
    tx = int(subprocess.check_output(net_tx, shell=True))
    return {"network_rx_bytes": rx, "network_tx_bytes": tx}
  except Exception as e:
    return {"network_rx_bytes": 0, "network_tx_bytes": 0}
    
def network_delta(container_id, previous_net):
    current = network_query(container_id)
    now = time.time()

    rx = current["network_rx_bytes"]
    tx = current["network_tx_bytes"]

    if container_id in previous_net:
        prev = previous_net[container_id]

        delta_rx = rx - prev["rx"]
        delta_tx = tx - prev["tx"]
        delta_time = now - prev["time"]
        if delta_rx < 0: delta_rx = 0
        if delta_tx < 0: delta_tx = 0

        rx_rate = delta_rx / delta_time if delta_time > 0 else 0
        tx_rate = delta_tx / delta_time if delta_time > 0 else 0
    else:
        delta_rx = 0 
        delta_tx = 0
        rx_rate = 0 
        tx_rate = 0 
    previous_net[container_id] = {
        "rx": rx,
        "tx": tx,
        "time": now
    }

    return {
        "network_rx_bytes": rx,
        "network_tx_bytes": tx,
        "delta_rx_bytes": delta_rx,
        "delta_tx_bytes": delta_tx,
        "rx_rate": rx_rate,
        "tx_rate": tx_rate
    }

def all_tools(container_id, prev_net):
  res = resource_query(container_id)
  #net = network_delta(container_id)
  net = network_delta(container_id, prev_net)
  res.update(net)
  write_file(res)

#def unpack_list(data):
  #for item in data:
    #if isinstance(item, dict):
      #return item
    
def write_file(result):
  '''maybe append all entries to one file'''

  timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S.%f")[:-4]
  result["time"] = timestamp

  container_id = result["id"]

  os.makedirs(f"system_logs/{result['name']}", exist_ok=True)

  output_file = f"system_logs/{result['name']}/{container_id}.jsonl"
  with open(output_file, "a") as f:
    json.dump(result, f)
    f.write("\n")


def parallel_work(ids):
  
  #container_ids = find_containerID(ids)
  #query = network_query(container_ids)
  workers = min(len(ids), os.cpu_count())
  #create_folders(ids)
  print(f"\nworkers: {workers}\n")
  with Manager() as manager:
    previous_net = manager.dict()
    with multiprocessing.Pool(workers) as pool:
        try:
          while True:
            #pool.map(all_tools, ids)
            pool.starmap(all_tools, [(cid, previous_net) for cid in ids])
            time.sleep(2)
        except KeyboardInterrupt:
            print("Terminated all queries")
            pool.terminate()
            pool.join()


if __name__ == "__main__":
  cids = find_containerID()
  parallel_work(cids)
  #print(network_query)
  #container_ids = find_containerID()
  #print(network_query(container_ids))
  #create_folders(container_ids)
  #parallel_work(container_ids)
