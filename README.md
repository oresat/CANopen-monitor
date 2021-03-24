# CANOpen Monitor

[![license](https://img.shields.io/github/license/oresat/CANopen-monitor)](./LICENSE)
[![pypi](https://img.shields.io/pypi/v/canopen-monitor)](https://pypi.org/project/canopen-monitor)
[![read the docs](https://readthedocs.org/projects/canopen-monitor/badge/?version=latest)](https://canopen-monitor.readthedocs.io)
[![issues](https://img.shields.io/github/issues/oresat/CANopen-monitor/bug?label=issues)](https://github.com/oresat/CANopen-monitor/issues?q=is%3Aopen+is%3Aissue+label%3Abug)
[![feature requests](https://img.shields.io/github/issues/oresat/CANopen-monitor/feature%20request?color=purple&label=feature%20requests)](https://github.com/oresat/CANopen-monitor/labels/feature%20request)
[![unit tests](https://img.shields.io/github/workflow/status/oresat/CANopen-monitor/Unit%20Tests?label=unit%20tests)](https://github.com/oresat/CANopen-monitor/actions?query=workflow%3A%22Unit+Tests%22)
[![deployment](https://img.shields.io/github/workflow/status/oresat/CANopen-monitor/Deploy%20to%20PyPi?label=deployment)](https://github.com/oresat/CANopen-monitor/actions?query=workflow%3A%22Deploy+to+PyPi%22)

An NCurses-based TUI application for tracking activity over the CAN bus and decoding messages with provided EDS/OD files.

***

# Quick Start

### Install

`$` `pip install canopen-monitor`

### Run

**Run the monitor, binding to `can0`**

`$` `canopen-monitor -i can0`

**Use this for an extensive help menu**

`$` `canopen-monitor --help`

***

# Configuration
The default configurations provided by CANOpen Monitor can be found in
[canopen_monitor/assets](./canopen_monitor/assets). These are the default
assets provided. At runtime these configs are copied to
`~/.config/canopen-monitor` where they can be modified and the changes
will persist.

EDS files are loaded from `~/.cache/canopen-monitor`
***

# Development and Contribution

### Documentation

Check out our [Read The Docs](https://canopen-monitor.readthedocs.io) pages for more info on the application sub-components and methods.

### Pre-Requisites
* Linux 4.11 or greater (any distribution)

* Python 3.8.5 or higher *(pyenv is recommended for managing different python versions, see [pyenv homepage](https://realpython.com/intro-to-pyenv/#build-dependencies) for information)*

### Install Locally

#### Setup a virtual CAN signal generator
`$` `sudo apt-get install can-utils`

#### Start a virtual CAN
`$` `sudo ip link add dev vcan0 type vcan`

`$` `sudo ip link set up vcan0`

#### Clone the repo
`$` `git clone https://github.com/Boneill3/CANopen-monitor.git`

`$` `cd CANopen-monitor`

`$` `pip install -e .[dev]`

*(Note: the `-e` flag creates a symbolic-link to your local development version. Set it once, and forget it)*

#### Generate random messages with socketcan-dev
`$` `chmod 700 socketcan-dev`

`$` `./socketcan-dev.py --random-id --random-message -r`

#### Start the monitor
`$` `canopen-monitor`

### Create documentation locally

`$` `make -C docs clean html`

*(Note: documentation is configured to auto-build with ReadTheDocs on every push to master)*

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
