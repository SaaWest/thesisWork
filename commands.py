import os
import subprocess
import json
import time
from datetime import datetime, timezone
import pathlib
import multiprocessing
import psutil

#pid = os.getpid()
#python_process = psutil.Process(pid)

def find_containerID():
  
  result = subprocess.check_output("docker ps -a | awk 'NR > 1 {print $1}'", shell=True).decode().strip()
  ids = [i for i in result.split('\n')]
  #print(repr(ids))
  return ids

def create_folders(ids):
  ids = find_containerID()
  for id in ids:
    #if not os.path.exists("system_logs/{id}"):
    os.makedirs(f"system_logs/{id}", exist_ok=True)

def network_query(container_ids):
  
  #container_ids = find_containerID()
  #create_folders(container_ids)
  #print("\nnetwork_query\n")
  #id_cycle_list = itertools.cycle(container_ids)

  try:
    #while True:
    #for id in container_ids:
      #timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S.%f")[:-4] 

      #output_file = f"system_logs/{id}/{id}_{timestamp}.json"

    query = f"SELECT basic.pid, stats.id, stats.name, stats.network_rx_bytes, stats.network_tx_bytes, " \
      + f"stats.memory_usage, stats.disk_read, stats.disk_write, (((stats.cpu_total_usage - stats.pre_cpu_total_usage)*1.0 / " \
      + f"(stats.system_cpu_usage - stats.pre_system_cpu_usage)*1.0) * online_cpus)*100 AS cpu_percent_used " \
      + f"FROM docker_container_stats AS stats JOIN " \
      + f"docker_containers AS basic ON stats.id = basic.id WHERE basic.id='{container_ids}'"
    result = subprocess.run(["osqueryi", '--json', query], check=True, capture_output=True, text=True)
    #print(type(result))
    #time.sleep(2)
    #result = multiprocessing.Process(target="osqueryi")
    #result_file = json.loads(result.stdout)
    #print(result_file[0]["id"])
    return result
    #result_file = json.loads(result.stdout)
    #with open(output_file, 'w') as f:
      #for id in container_ids:
        #if id in f"system_logs/{id}":
          #json.dump(result_file, f, indent=4)

      #time.sleep(10)

  except Exception as e:
    print(F"\nTerminated safely: {e}\n")

def unpack_list(data):
  for item in data:
    if isinstance(item, dict):
      return item
    
def write_file(result):
  result_file = json.loads(result.stdout)
  #print(type(result_file))
  timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S.%f")[:-4]
  result_file[0]["time"] = timestamp
  unpacked = unpack_list(result_file)
  container_id = result_file[0]["id"]
  #timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S.%f")[:-4]
  os.makedirs(f"system_logs/{result_file[0]["name"]}", exist_ok=True)
  #create_folders(id)
  output_file = f"system_logs/{result_file[0]["name"]}/{container_id}.jsonl"
  if not os.path.exists(output_file):
    with open(output_file, 'w') as f:
      json.dump(unpacked, f, indent=4)
      f.write("\n")
  else:
    if result_file is not None:
      with open(output_file, "a") as f:
        json.dump(unpacked, f, indent=4)
        f.write("\n")


def parallel_work(ids):
  
  #container_ids = find_containerID(ids)
  #query = network_query(container_ids)
  workers = os.cpu_count()
  #create_folders(ids)
  print(f"\nworkers: {workers}\n")
  with multiprocessing.Pool(processes=workers) as mp:
    while True:
      try:
        result = mp.map(network_query, ids)
        for cont_id in result:
          write_file(cont_id)
          #memory_use_mib = python_process.memory_info()[0] / (1024 * 1024)
          #cpu_percent = python_process.cpu_percent(interval=1)
          #print(f"Memory Use: {memory_use_mib:.2f} MiB | CPU Percent: {cpu_percent}%")
        time.sleep(2)
      except KeyboardInterrupt:
        print("\nTerminated safely\n")
        mp.terminate()
        mp.join()


if __name__ == "__main__":
  container_ids = find_containerID()
  #create_folders(container_ids)
  parallel_work(container_ids)
