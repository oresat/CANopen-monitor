# CANOpen Monitor

[![License](https://img.shields.io/github/license/oresat/CANopen-monitor)](./LICENSE)
[![PyPi](https://img.shields.io/pypi/pyversions/canopen-monitor?label=pypi)](https://pypi.org/project/canopen-monitor)
[![Trello](https://img.shields.io/badge/Trello-Backlog-blue)](https://trello.com/b/PWuRFBh1/canopen-monitor)
[![Unit Tests](https://img.shields.io/github/workflow/status/oresat/CANopen-monitor/Unit%20Tests?label=unit%20tests)](https://github.com/oresat/CANopen-monitor/actions?query=workflow%3A%22Unit+Tests)
[![Build](https://img.shields.io/github/workflow/status/oresat/CANopen-monitor/Upload%20Python%20Package)](https://github.com/oresat/CANopen-monitor/actions?query=workflow%3A%22Upload+Python+Package)
[![Issues](https://img.shields.io/github/issues/oresat/CANopen-monitor)](https://github.com/oresat/CANopen-monitor/issues)

A utility for displaying and tracking activity over the CAN bus.

***

# Run App

`$` `canopen-monitor`

***

# Install via PyPi

`$` `pip3 install canopen-monitor`

***

# Install Locally

**Build the CANOpen Monitor module:**

`$` `python3 setup.py sdist bdist_wheel`

**Install for current user only:**

`$` `python -m pip install dist/*.whl`

**Install for all users:**

`$` `sudo python -m pip install dist/*.whl`

**Clean up build artifacts:**

`$` `rm -rf build dist *.egg-info`

***

# Development and Contribution:

**Install dependencies:**

`$` `pip install -r requirements.txt`


**Install development dependencies:**

`$` `pip install -r dev-requirements.txt`

**Lint Code:**

`$` `flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics`

**Run unit tests:**

`$` `python -m unittest -f --locals tests/*.py`

**Auto generate Sphinx documentation:**

`$` `sphinx-apidoc -o docs/source canopen_monitor`

`$` `make -C docs clean html`

**Deploy manually to PyPi:**

`$` `python -m twine upload dist/*`

*(This assumes that you have the correct PyPi credentials and tokens set up according to the instructions [outlined here](https://packaging.python.org/guides/distributing-packages-using-setuptools/#id79))*

***

# Configs:

  These are the auto-generated configs that are stored in `~/.config/canopen-monitor`

`devices.json:`
```json
[
  "can0"
]
```
A list of CAN Buses that CAN Monitor will try to bind to on launch.

*(note: additional buses can be added via cmd-line arguments, see `canopen-monitor --help`)*

&nbsp;

`layout.json`
```json
{
  "type": "grid",
  "split": "horizontal",
  "data": [{
    "type": "grid",
    "split": "vertical",
    "data": [{
    "type": "table",
    "capacity": 16,
    "dead_node_timeout": 600,
    "name": "Hearbeats",
    "stale_node_timeout": 60,
    "fields": [],
    "frame_types": ["HB"]
    }, {
    "type": "table",
    "capacity": 16,
    "dead_node_timeout": 600,
    "name": "Info",
    "stale_node_timeout": 60,
    "fields": [],
    "frame_types": []
    }]
  }, {
    "type": "table",
    "capacity": 16,
    "dead_node_timeout": 60,
    "name": "Misc",
    "stale_node_timeout": 600,
    "fields": [],
    "frame_types": [
    "NMT",
    "SYNC",
    "EMCY",
    "TIME",
    "TPDO1",
    "RPDO1",
    "TPDO2",
    "RPDO2",
    "TPDO3",
    "RPDO3",
    "TPDO4",
    "RPDO4",
    "TSDO",
    "RSDO",
    "UKOWN"
    ]
  }]
}
```
A recursive set of dictionaries that define how CAN Monitor constructs the UI layout as well as some other properties of each table.

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
