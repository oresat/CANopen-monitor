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

# Configuration

The default configurations provided by CANOpen Monitor can be found in [canopen_monitor/assets](./canopen_monitor/assets). These are the default assets provided, at runtime these configs are copied to `~/.config/canopen-monitor` where they can be changed persistently.

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
