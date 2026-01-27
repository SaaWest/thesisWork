import os
import subprocess
from dotenv import load_dotenv
import json
import time
from datetime import datetime

def find_containerID():
 load_dotenv()
 #password = os.getenv("DB_PASSWORD")
 #print(password)
 #env = os.environ.copy()
 #env["DB_PASSWORD"] = password

#result = subprocess.check_output(["sudo docker ps -a | awk 'NR > 1 {print $1}'"], shell=True, env=env).decode().strip()
 result = subprocess.check_output("docker ps -a | awk 'NR > 1 {print $1}'", shell=True).decode().strip()
 print(result)
 return result

def network_query(container_id):
 container_id = find_containerID()

 load_dotenv()
 password = os.getenv("DB_PASSWORD")
 env = os.environ.copy()
 env["DB_PASSWORD"] = password

 #net_query = f"SELECT name, network_rx_bytes, network_tx_bytes FROM docker_container_stats WHERE id = '{container_id}';"
 #print("net query" + net_query)
 try:
  while True:

   timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S") 

   output_file = f"system_logs/networkLog_{timestamp}.json"
   query = f"SELECT name, network_rx_bytes, network_tx_bytes, cpu_total_usage, memory_usage FROM docker_container_stats WHERE id='{container_id}'"
   #query = f"SELECT name, network_rx_bytes, network_tx_bytes, (((cpu_total_usage-pre_cpu_usage)*1.0 / (system_cpu_usage-pre_system_cpu_usage)*1.0) * online_cpus) * 100 AS usage, memory_usage FROM docker_container_stats WHERE id='{container_id}';"
   #command = f'echo "{password}" | sudo -S osqueryi --json "{query}" > {output_file}'
   result = subprocess.run(["osqueryi", '--json', query], check=True, capture_output=True, text=True)
   #print('success')
   result_file = json.loads(result.stdout)
   with open(output_file, 'w') as f:
    json.dump(result_file, f, indent=4)

   time.sleep(10)

 except KeyboardInterrupt:
  print("done\n")

if __name__ == "__main__":
 container_id = find_containerID()
 network_query(container_id)
