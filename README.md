# CANOpen Monitor

[![license](https://img.shields.io/github/license/oresat/CANopen-monitor)](./LICENSE)
[![pypi](https://img.shields.io/pypi/v/canopen-monitor)](https://pypi.org/project/canopen-monitor)
[![read the docs](https://readthedocs.org/projects/canopen-monitor/badge/?version=latest)](https://canopen-monitor.readthedocs.io/en/latest/?badge=latest)
[![issues](https://img.shields.io/github/issues/oresat/CANopen-monitor/bug?label=issues)](https://github.com/oresat/CANopen-monitor/issues?q=is%3Aopen+is%3Aissue+label%3Abug)
[![unit tests](https://img.shields.io/github/workflow/status/oresat/CANopen-monitor/Unit%20Tests?label=unit%20tests)](https://github.com/oresat/CANopen-monitor/actions?query=workflow%3A%22Unit+Tests%22)
[![deployment](https://img.shields.io/github/workflow/status/oresat/CANopen-monitor/Deploy%20to%20PyPi?label=deployment)](https://github.com/oresat/CANopen-monitor/actions?query=workflow%3A%22Deploy+to+PyPi%22)

A utility for displaying and tracking activity over the CAN bus.

***

# Quick Start *(Usage)*

## Install *(from PyPi)*

`$` `pip install package-demo`


## Run

`$` `canopen-monitor`

***

# Development and Contribution

## Build

`$` `python setup.py bdist_wheel sdist`

## Install Locally

`$` `pip install -e .[dev]`

*(The `-e` flag creates a symbolic-link to your local development version, so there's no need to uninstall and reinstall every time. Set it and forget it.)*

## Create or Update Manifest

`$` `rm -f MANIFEST.in && check-manifest --update`

## Create or Update Sphinx Documentation

`$` `sphinx-apidoc -f -o docs canopen_monitor && make -C docs html`

***

# Default Configs

These are the auto-generated configs that can be found at `~/.config/canopen-monitor/`

`devices.json:`
```json
{
  "dead_timeout": 120,
  "devices": [
    "can0"
  ],
  "stale_timeout": 60
}
```
A set of devices configs including a list of CAN Buses that CAN Monitor will try to bind to on launch as well as respective timeout lengths.

*(note: additional buses can be added via cmd-line arguments, see `canopen-monitor --help`)*

&nbsp;

`layout.json`
```json
{
  "data": [
    {
      "data": [
        {
          "capacity": null,
          "fields": {
            "COB ID": "arb_id", 
            "Node Name": "node_name", 
            "Interface": "interface", 
            "State": "status", 
            "Status": "parsed_msg"
            },
          "frame_types": [
            "HEARTBEAT"
          ],
          "name": "Hearbeats",
          "type": "message_table"
        },
        {
        "capacity": null,
        "fields": [],
        "frame_types": [],
        "name": "Info",
        "type": "message_table"
        }
      ],
      "split": "vertical",
      "type": "grid"
    },
    {
      "capacity": null,
      "fields": {
            "COB ID": "arb_id", 
            "Node Name": "node_name", 
            "Interface": "interface", 
            "Type": "message_type", 
            "Time Stamp": "timestamp",
            "Message": "parsed_msg"
            },
      "frame_types": [
        "NMT",
        "SYNC",
        "TIME",
        "EMER",
        "PDO1_TX",
        "PDO1_RX",
        "PDO2_TX",
        "PDO2_RX",
        "PDO3_TX",
        "PDO3_RX",
        "PDO4_TX",
        "PDO4_RX",
        "SDO_TX",
        "SDO_RX",
        "UKNOWN"
      ],
      "name": "Misc",
      "type": "message_table"
    }
  ],
  "split": "horizontal",
  "type": "grid"
}
```
A recursive set of dictionaries that define how CAN Monitor constructs the UI layout and what CAN Message types go to what tables.

&nbsp;

`nodes.json`
```json
{
  "64": "MDC"
}
```
A list of COB ID's in decimal notation that have a paired name which will override the default display name of that node in CAN Monitor.

***

### Message Types + COB ID Ranges:

###### [Wikipedia Table](https://en.wikipedia.org/wiki/CANopen#Predefined_Connection_Set.5B7.5D)

###### Abridged Table:

| Name            | COB ID Range |
|-----------------|--------------|
| SYNC            | 080          |
| EMCY            | 080 + NodeID |
| TPDO1           | 180 + NodeID |
| RPDO1           | 200 + NodeID |
| TPDO2           | 280 + NodeID |
| RPDO2           | 300 + NodeID |
| TPDO3           | 380 + NodeID |
| RPDO3           | 400 + NodeID |
| TPDO4           | 480 + NodeID |
| RPDO4           | 500 + NodeID |
| TSDO            | 580 + NodeID |
| RSDO            | 600 + NodeID |
| NMT (Heartbeat) | 700 + NodeID |
