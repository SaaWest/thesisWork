import json
from pathlib import Path
import pandas
import os

class Ratio_Alert():
    def __init__(self, log_dir):
    #file_path = "system_logs/ab2e7b0ad971/ab2e7b0ad971_2026-02-09_19:56:21.62"
        self.system_logs = Path(log_dir)
        self.dir_paths = list(self.system_logs.glob("*/*.jsonl"))
        #self.data = pandas.DataFrame()
        self.data = []

    def read_data(self):
        try:
            for path in self.dir_paths:
                try:
                    with open(path, 'r') as f:
                        for line in f:
                            """Make Condition where only new instances of time with id allow object to be appended"""
                            """Example if line[time] and line[id] not in self.data:"""
                            print(line)
                            self.data.append(json.loads(line))
                    #panda_data = pandas.read_json(str(path), lines=True)
                    #print(panda_data)
                    #self.data = pandas.concat([self.data, panda_data], ignore_index=True)
                except ValueError as e:
                    print(f"Error reading JSON in {str(path)}: {e}")
        except json.JSONDecodeError as e:
            print(f"Error: {e}")

    def print_data(self):
        for i in self.data:
            print(f"{i}")
        
    def calculate_ratio_cpu_memory(self, ):
        cpu = float(self.data[0].get("cpu_percent_used"))
        memory_gb = int(self.data[0].get("memory_usage")) *  0.001048576#* 1.048576
        cpu_mem_ratio = memory_gb / cpu

        return (cpu, memory_gb)




if __name__ == "__main__":
    ratio = Ratio_Alert("system_logs/")
    #ratio.append_dir_paths()
    #print(ratio.dir_paths)
    ratio.read_data()
    #ratio.calculate_ratio_cpu_memory()
    #print(ratio.calculate_ratio_cpu_memory())
    #print(ratio.data)
    #ratio.print_data()

