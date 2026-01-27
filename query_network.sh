#!/bin/bash
source .env

output=$(python3 commands.py)
container_id="$output"

while true
do
	timestamp=$(date +"%Y-%m-%d_%H:%M:%S")
	echo "$DB_PASSWORD" | sudo -S osqueryi --json "SELECT name, network_rx_bytes, network_tx_bytes FROM docker_container_stats WHERE id = '$container_id';" > "system_logs/networkLog_$timestamp.json"
	sleep 10

done
echo "success"
