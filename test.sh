#!/bin/bash
path="/usr/bin/osqueryi"

query="SELECT name, network_rx_bytes, network_tx_bytes FROM docker_container_stats WHERE id='e4d738c5a2c5'";

"$path" "$query"
