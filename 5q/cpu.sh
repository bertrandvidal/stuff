#!/bin/bash

PORT=$(cat ~/.quio/q-api-port.txt)
CPU_PERCENT=$(ps -A -o %cpu | awk '{s+=$1} END {print s}')

for i in `seq 0 9`
    do
        [[ $((i * 10)) -le ${CPU_PERCENT%.*} ]] && COLOR=008800 || COLOR=000000
        curl -H 'Content-Type: application/json' \
             -X POST http://localhost:$PORT/api/1.0/signals \
             -d '{"name": "CPU usage", "pid": "DK5QPID", "zoneId": "'"KEY_$((i + 1))"'", "color": "#'"$COLOR"'"}' 1>/dev/null 2>&1
    done

