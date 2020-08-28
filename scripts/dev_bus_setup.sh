#!/usr/bin/env bash

BUS_LIST_PATH=~/.config/canopen-monitor/devices.json
BUS_LIST=$(cat $BUS_LIST_PATH | cut -d'[' -f1 | cut -d']' -f1 | sed 's/,//g' | xargs)

for bus in ${BUS_LIST[@]}; do
  sudo ip link add $bus type vcan > /dev/null 2>&1
  if [[ $? == 0 ]]; then
    echo -e "Created bus: $bus"
  else
    echo -e "Failed to create bus: $bus"
  fi

  sudo ip link set $bus up > /dev/null 2>&1
  if [[ $? == 0 ]]; then
    echo -e "Set bus status to UP"
  else
    echo -e "Failed to set bus status to UP"
  fi
done
