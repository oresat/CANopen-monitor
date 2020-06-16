# CANopen-monitor

A utility for displaying and tracking activity over the CAN bus.

### Installation

  __(Manual) Git Installation:__

  Clone the repo:

  `$` `git clone https://github.com/oresat/CANopen-monitor.git`

  Run the local start script:

  `$` `./CANopen-monitor/can-monitor`

***

### Usage

  Start can-monitor tool:
  * `$` `can-monitor`

***

### Configs:

  The config files are by default stored in `~/.canmon`

#### Defaults:
###### `~/.canmon/devices.json`
```json
[
  "can0"
]
```

&nbsp;

###### `~/.canmon/layout.json`
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

***

### Node IDs/Frame Types:

###### [Wikipedia Table](https://en.wikipedia.org/wiki/CANopen#Predefined_Connection_Set.5B7.5D)

###### Abridged Table:

  * **Hearbeat:** `0x701 - 0x7FF`
  * **PDO:** `0x181 - 0x57F`
  * **SDO:**
    * _tx:_ `0x581 - 0x5FF`
    * _rx:_ `0x601 - 0x67F`
