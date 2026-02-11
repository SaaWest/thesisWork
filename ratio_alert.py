import json
from pathlib import Path
import os

class Ratio_Alert():
    def __init__(self, log_dir):
    #file_path = "system_logs/ab2e7b0ad971/ab2e7b0ad971_2026-02-09_19:56:21.62"
        self.system_logs = Path(log_dir)
        self.dir_paths = list(self.system_logs.glob("*/*.jsonl"))
        self.data = ""

    def append_data(self):
        try:
            for path in self.dir_paths:
                with path.open('r') as file:
                    for line in file:
                        line = line.strip()
                        if line:
                            reader = json.loads(line)
                            print(reader)
                        #self.data += reader
                        #print(type(self.data))
        except json.JSONDecodeError as e:
            print(f"Error: {e}")

    def print_data(self):
        for i in self.data:
            print(f"\n{i}")
        
    def calculate_ratio_cpu_memory(self):
        cpu = float(self.data[0].get("cpu_percent_used"))
        memory_gb = int(self.data[0].get("memory_usage")) *  0.001048576#* 1.048576
        cpu_mem_ratio = memory_gb / cpu

        #for val in element.values():
            #if val == "cpu_percent_used":
                #cpu = float(val)
            #if val == "memory_usage":
                #memory = int(val)

        return (cpu, memory_gb)




if __name__ == "__main__":
    ratio = Ratio_Alert("system_logs/")
    #ratio.append_dir_paths()
    #print(ratio.dir_paths)
    ratio.append_data()
    #ratio.calculate_ratio_cpu_memory()
    #print(ratio.calculate_ratio_cpu_memory())
    #ratio.print_data()

