import json
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import sys

def graph_resources(file_path):
    
    """
    Reads a JSON-lines file with resource metrics and plots CPU, memory,
    disk, and network usage over time.
    
    :param file_path: Path to the JSON-lines file
    """
    data = []

    # Read JSON-lines file
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                entry = json.loads(line)
                data.append(entry)

    if not data:
        print("No data found in file.")
        return

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Convert numeric fields
    numeric_cols = ['cpu_percent', 'mem_percent', 'disk_read', 'disk_write',
                    'network_rx_bytes', 'network_tx_bytes']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Convert time field to datetime
    df['time'] = pd.to_datetime(df['time'], format='%Y-%m-%d_%H:%M:%S.%f')

    # Set time as index for plotting
    df.set_index('time', inplace=True)

    # Plot each resource
    plt.figure(figsize=(15, 10))

    # CPU and Memory
    plt.subplot(2, 2, 1)
    plt.plot(df.index, df['cpu_percent'], label='CPU %')
    plt.plot(df.index, df['mem_percent'], label='Memory %')
    plt.title('CPU & Memory Usage Over Time')
    plt.xlabel('Time')
    plt.ylabel('% Usage')
    plt.legend()
    plt.grid(True)

    # Disk I/O
    plt.subplot(2, 2, 2)
    plt.plot(df.index, df['disk_read'], label='Disk Read')
    plt.plot(df.index, df['disk_write'], label='Disk Write')
    plt.title('Disk I/O Over Time')
    plt.xlabel('Time')
    plt.ylabel('Bytes')
    plt.legend()
    plt.grid(True)

    # Network
    plt.subplot(2, 2, 3)
    plt.plot(df.index, df['network_rx_bytes'], label='Network RX')
    plt.plot(df.index, df['network_tx_bytes'], label='Network TX')
    plt.title('Network Traffic Over Time')
    plt.xlabel('Time')
    plt.ylabel('Bytes')
    plt.legend()
    plt.grid(True)

    plt.subplot(2, 2, 4)
    plt.plot(df.index, df['rx_rate'], label='Network RX rate')
    plt.plot(df.index, df['tx_rate'], label='Network TX rate')
    plt.title('Network Traffic Over Time')
    plt.xlabel('Time')
    plt.ylabel('Bytes')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()

# Example usage:
# graph_resources('container_metrics.jsonl')
if __name__=="__main__":
    file_path = sys.argv[1]
    graph_resources(file_path)