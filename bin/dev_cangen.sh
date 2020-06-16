#!/usr/bin/env bash

BUS_LIST_PATH=~/.canmon/devices.json
BUS_LIST=$(cat $BUS_LIST_PATH | cut -d'[' -f1 | cut -d']' -f1 | sed 's/,//g' | xargs)
PID_LIST=()

for bus in ${BUS_LIST[@]}; do
  cangen $bus &
  PID_LIST+=($!)
done

echo -e "Spawned three test devices: (${BUS_LIST[@]}):(${PID_LIST[@]})"

while [[ 1 ]]; do
  read -p '> ' input
  input=$(echo $input | xargs)

  if [[ $input == "q" ]] || [[ $input == 'quit' ]]; then
    for pid in ${PID_LIST[@]}; do
      kill -9 $pid
    done

    exit 0
  fi
done
