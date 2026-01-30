import os
import subprocess
import json
import time
from datetime import datetime, timezone
import itertools
import multiprocessing

def find_containerID():
  
  result = subprocess.check_output("docker ps -a | awk 'NR > 1 {print $1}'", shell=True).decode().strip()
  ids = [i for i in result.split('\n')]
  #print(repr(ids))
  return ids

def create_folders(ids):
  ids = find_containerID()
  for id in ids:
    if not os.path.exists("system_logs/{id}"):
      os.mkdir(f"system_logs/{id}")

def network_query(container_ids):
  
  container_ids = find_containerID()
  id_cycle_list = itertools.cycle(container_ids)

  try:
    while True:
      for id in id_cycle_list:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S.%f")[:-4] 

        output_file = f"system_logs/{id}/{id}_{timestamp}.json"

        query = f"SELECT basic.pid, stats.name, stats.network_rx_bytes, stats.network_tx_bytes, " \
          + f"stats.memory_usage, stats.memory_max_usage, (((stats.cpu_total_usage - stats.pre_cpu_total_usage)*1.0 / " \
          + f"(stats.system_cpu_usage-stats.pre_system_cpu_usage)*1.0) * online_cpus)*100 AS cpu_percent_used " \
          + f"FROM docker_container_stats AS stats JOIN " \
          + f"docker_containers AS basic ON stats.id = basic.id WHERE basic.id='{id}'"
        #query = f"SELECT name, network_rx_bytes, network_tx_bytes, (((cpu_total_usage-pre_cpu_usage)*1.0 / (system_cpu_usage-pre_system_cpu_usage)*1.0) * online_cpus) * 100 AS usage, memory_usage FROM docker_container_stats WHERE id='{container_id}';"
        #command = f'echo "{password}" | sudo -S osqueryi --json "{query}" > {output_file}'
        result = subprocess.run(["osqueryi", '--json', query], check=True, capture_output=True, text=True)
        #time.sleep(2)
        #result = multiprocessing.Process(target="osqueryi")
        result_file = json.loads(result.stdout)
        with open(output_file, 'w') as f:
          json.dump(result_file, f, indent=4)

        #time.sleep(10)

  except KeyboardInterrupt:
    print("\nTerminated safely\n")

if __name__ == "__main__":
  container_ids = find_containerID()
  create_folders(container_ids)
  cpu_workers = min(multiprocessing.cpu_count(), 2)
  with multiprocessing.Pool(processes=cpu_workers) as multi_pool:
    #while True: 
    multi_pool.map(network_query, container_ids)
    time.sleep(2)
